from datetime import datetime

from sqlalchemy import BigInteger, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from database import Base


class Account(Base):
    __tablename__ = "accounts"

    __table_args__ = (
        CheckConstraint(
            "balance_pence >= 0",
            name="ck_accounts_nonnegative_balance"
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    owner_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    balance_pence: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        default=0,
        server_default="0"
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    account_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("accounts.id"),
        nullable=False
    )

    transaction_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    amount_pence: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now()
    )
