from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.categorize import categorize_merchant
from app.celery_app import celery_app
from app.db import SessionLocal
from app.models import Transaction
from app.parsers import millennium, revolut

PARSERS = {"millennium": millennium.parse, "revolut": revolut.parse}


@celery_app.task(name="app.tasks.import_statement")
def import_statement(bank: str, raw_bytes: bytes) -> dict:
    """
    Parsuje wyciag, wrzuca do bazy z ON CONFLICT DO NOTHING po dedup_hash
    (ten sam plik wgrany dwa razy nie zduplikuje transakcji).
    """
    parser = PARSERS.get(bank)
    if parser is None:
        return {"error": f"nieznany bank: {bank}"}

    rows = parser(raw_bytes)
    inserted = 0

    with SessionLocal() as db:
        for row in rows:
            stmt = (
                pg_insert(Transaction)
                .values(
                    source_bank=row.source_bank,
                    tx_date=row.tx_date,
                    amount=row.amount,
                    fee=row.fee,
                    currency=row.currency,
                    description_raw=row.description_raw,
                    merchant_clean=row.merchant_clean,
                    category=row.category,
                    is_transfer=row.is_transfer,
                    status=row.status,
                    dedup_hash=row.dedup_hash,
                    raw=row.raw,
                )
                .on_conflict_do_nothing(index_elements=["dedup_hash"])
            )
            result = db.execute(stmt)
            inserted += result.rowcount
        db.commit()

    # dlugi ogon leci do kategoryzacji Ollama jako osobne zadanie w tle,
    # zeby import nie czekal na inferencje modelu wiersz po wierszu
    categorize_uncategorized.delay()

    return {"parsed": len(rows), "inserted": inserted}


@celery_app.task(name="app.tasks.categorize_uncategorized")
def categorize_uncategorized(batch_size: int = 200) -> dict:
    updated = 0
    with SessionLocal() as db:
        pending = (
            db.query(Transaction)
            .filter(
                Transaction.category == "other.uncategorized",
                Transaction.is_transfer.is_(False),
            )
            .limit(batch_size)
            .all()
        )
        for tx in pending:
            guess = categorize_merchant(tx.merchant_clean or tx.description_raw)
            if guess.confidence >= 0.5:
                tx.category = guess.category
                updated += 1
        db.commit()

    return {"checked": len(pending), "updated": updated}
