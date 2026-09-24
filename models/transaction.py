from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from utils.enums import TransactionType


@dataclass
class Transaction:
    """
    Represents a financial transaction.
    """
    id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    category_id: UUID
    description: str | None
    transaction_date: date


@dataclass
class TransactionSummary:
    """
    Represents a transaction with the category name included
    for display and reporting purposes.
    """
    id: UUID
    user_id: UUID
    amount: Decimal
    currency: str
    transaction_type: TransactionType
    category_id: UUID
    category_name: str
    description: str | None
    transaction_date: date


@dataclass
class Category:
    """
    Represents a transaction category.
    """
    id: UUID
    user_id: UUID | None
    category_name: str
    transaction_type: TransactionType