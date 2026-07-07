import hashlib
import os
import re
from dataclasses import dataclass, field
from datetime import date

POSTAL_CODE_RE = re.compile(r"\d{2}-\d{3}")
DIGITS_RE = re.compile(r"\d+")
WHITESPACE_RE = re.compile(r"\s+")


@dataclass
class NormalizedRow:
    """Wspolny ksztalt wiersza, niezaleznie od banku zrodlowego."""

    source_bank: str
    tx_date: date
    amount: float
    currency: str
    description_raw: str
    fee: float | None = None
    status: str = "completed"
    is_transfer: bool = False
    category: str = "other.uncategorized"
    merchant_clean: str = field(init=False, default="")
    raw: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.merchant_clean = clean_merchant(self.description_raw)

    @property
    def dedup_hash(self) -> str:
        key = f"{self.source_bank}|{self.tx_date}|{self.amount}|{self.description_raw}"
        return hashlib.sha256(key.encode("utf-8")).hexdigest()


def clean_merchant(description: str) -> str:
    """
    Millennium duplikuje nazwe sprzedawcy i dokleja kod pocztowy w opisie,
    np. "CARREFOUR HIPERMARKET CARREFOUR HIPERMARKET 97-500 RADOMSKO".
    Usuwamy kod pocztowy, cyfry i powtorzony fragment nazwy.
    """
    text = POSTAL_CODE_RE.sub("", description)
    text = DIGITS_RE.sub("", text)
    text = WHITESPACE_RE.sub(" ", text).strip()

    words = text.split(" ")
    half = len(words) // 2
    if half > 0 and words[:half] == words[half : half * 2]:
        text = " ".join(words[:half])

    return text.strip().upper()


FAMILY_SURNAMES_ENV = "MONEY_MAP_FAMILY_SURNAMES"  # np. "ARCZEWSKI", ustaw w .env


def is_family_or_own_transfer(description: str, tx_type: str) -> bool:
    """
    Heurystyka na przelewy rodzinne / miedzy wlasnymi kontami.

    Dwa niezalezne sygnaly, bo typ transakcji sam w sobie nie zawsze wystarcza:
    1. Sam "Rodzaj"/"Rodzaj transakcji" juz to zdradza: "Zasilenie" (Revolut,
       doladowanie z wlasnej karty), "PRZELEW NA TELEFON"/"PRZELEW SRODKOW"
       (Millennium). Revolutowe bare "Przelew" NIE jest tu wystarczajace samo
       w sobie, bo to samo "Przelew" pokrywa tez zwykle platnosci do obcych.
    2. Opis/kontrahent zawiera nazwisko z listy w MONEY_MAP_FAMILY_SURNAMES
       (comma-separated w .env, pusta domyslnie, nie zakladamy niczyich danych).
    """
    type_markers = ("zasilenie", "przelew na telefon", "przelew srodkow", "przelew środków")
    if any(marker in tx_type.lower() for marker in type_markers):
        return True

    surnames = [
        s.strip().upper()
        for s in os.environ.get(FAMILY_SURNAMES_ENV, "").split(",")
        if s.strip()
    ]
    return any(surname in description.upper() for surname in surnames)
