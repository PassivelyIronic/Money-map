from pathlib import Path

from app.parsers import millennium, revolut

FIXTURES = Path(__file__).parent / "fixtures"


def test_millennium_parses_and_coalesces_amount():
    raw = (FIXTURES / "millennium_sample.csv").read_bytes()
    rows = millennium.parse(raw)

    assert len(rows) == 3
    debit, _, credit = rows
    assert debit.amount == -1.00  # Obciazenia, juz ujemne
    assert credit.amount == 80.00  # Uznania


def test_millennium_cleans_duplicated_merchant_and_postal_code():
    raw = (FIXTURES / "millennium_sample.csv").read_bytes()
    rows = millennium.parse(raw)

    assert rows[1].merchant_clean == "CARREFOUR HIPERMARKET"


def test_millennium_flags_family_transfer(monkeypatch):
    monkeypatch.setenv("MONEY_MAP_FAMILY_SURNAMES", "ARCZEWSKI")
    raw = (FIXTURES / "millennium_sample.csv").read_bytes()
    rows = millennium.parse(raw)

    assert rows[2].description_raw == "ARCZEWSKI SZYMON"
    assert rows[2].is_transfer is True


def test_revolut_skips_non_completed_and_flags_topup():
    raw = (FIXTURES / "revolut_sample.csv").read_bytes()
    rows = revolut.parse(raw)

    assert len(rows) == 3  # wszystkie w fixture sa ZAKONCZONO
    assert rows[0].is_transfer is True  # Zasilenie
    assert rows[1].is_transfer is False  # OTP_PAYMENT
