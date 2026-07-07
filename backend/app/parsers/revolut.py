import csv
from datetime import datetime
from io import StringIO

from app.parsers.base import NormalizedRow, is_family_or_own_transfer

ENCODING = "utf-8"
DATE_FMT = "%d.%m.%Y %H:%M"
COMPLETED_STATE = "ZAKOŃCZONO"


def _to_float(value: str) -> float:
    return float(value.strip().replace(",", "."))


def parse(raw_bytes: bytes) -> list[NormalizedRow]:
    text = raw_bytes.decode(ENCODING)
    reader = csv.DictReader(StringIO(text), delimiter="\t")

    rows: list[NormalizedRow] = []
    for line in reader:
        # pomijamy pending/cofniete, licza sie tylko zakonczone transakcje
        if line["State"].strip().upper() != COMPLETED_STATE:
            continue

        tx_type = line["Rodzaj"].strip()
        fee_raw = line.get("Opłata", "0").strip()

        rows.append(
            NormalizedRow(
                source_bank="revolut",
                tx_date=datetime.strptime(
                    line["Data rozpoczęcia"].strip(), DATE_FMT
                ).date(),
                amount=_to_float(line["Kwota"]),
                fee=_to_float(fee_raw) if fee_raw else None,
                currency=line.get("Waluta", "PLN").strip() or "PLN",
                description_raw=line["Opis"].strip(),
                is_transfer=is_family_or_own_transfer(line["Opis"], tx_type),
                raw=dict(line),
            )
        )
    return rows
