import csv
from datetime import datetime
from io import StringIO

from app.parsers.base import NormalizedRow, is_family_or_own_transfer

DATE_FMT = "%d.%m.%Y"


def _decode(raw_bytes: bytes) -> str:
    """
    Nie mam pewności w jakim kodowaniu Millennium eksportuje u Ciebie plik
    (starsze polskie systemy bankowe czesto uzywaja cp1250, nowsze UTF-8).
    Probuje po kolei, zamiast zakladac jedno na sztywno.
    """
    for encoding in ("utf-8-sig", "cp1250", "latin-1"):
        try:
            return raw_bytes.decode(encoding)
        except UnicodeDecodeError:
            continue
    raise ValueError("nie udalo sie zdekodowac pliku w zadnym ze znanych kodowan")


def _to_float(value: str) -> float | None:
    value = value.strip().replace(" ", "").replace(",", ".")
    if not value:
        return None
    return float(value)


def parse(raw_bytes: bytes) -> list[NormalizedRow]:
    text = _decode(raw_bytes)
    reader = csv.DictReader(StringIO(text), delimiter="\t")

    rows: list[NormalizedRow] = []
    for line in reader:
        obciazenia = _to_float(line["Obciążenia"])
        uznania = _to_float(line["Uznania"])
        # dokladnie jedno z tych dwoch pol jest wypelnione,
        # obciazenia przychodzi juz jako wartosc ujemna
        amount = uznania if uznania is not None else obciazenia
        if amount is None:
            continue

        tx_type = line["Rodzaj transakcji"].strip()
        counterparty = line["Odbiorca/Zleceniodawca"].strip()
        rows.append(
            NormalizedRow(
                source_bank="millennium",
                tx_date=datetime.strptime(line["Data transakcji"].strip(), DATE_FMT).date(),
                amount=amount,
                currency=line.get("Waluta", "PLN").strip() or "PLN",
                description_raw=counterparty,
                is_transfer=is_family_or_own_transfer(counterparty, tx_type),
                raw=dict(line),
            )
        )
    return rows
