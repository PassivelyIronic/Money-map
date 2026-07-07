import uuid
from datetime import date

from sqlalchemy import Boolean, Date, Numeric, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    source_bank: Mapped[str] = mapped_column(String(32))  # millennium / revolut / ...
    tx_date: Mapped[date] = mapped_column(Date)  # data transakcji, nie rozliczenia
    amount: Mapped[float] = mapped_column(Numeric(12, 2))  # ze znakiem
    fee: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="PLN")

    description_raw: Mapped[str] = mapped_column(String)
    merchant_clean: Mapped[str | None] = mapped_column(String, nullable=True)

    category: Mapped[str] = mapped_column(String(64), default="other.uncategorized")
    is_transfer: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(32), default="completed")

    # hash(source_bank, tx_date, amount, description_raw), chroni przed
    # podwojnym importem tego samego wiersza z pokrywajacych sie eksportow
    dedup_hash: Mapped[str] = mapped_column(String(64), unique=True, index=True)

    raw: Mapped[dict] = mapped_column(JSONB)  # oryginalny wiersz, do debugowania

    def __repr__(self) -> str:
        return f"<Transaction {self.tx_date} {self.amount} {self.category}>"
