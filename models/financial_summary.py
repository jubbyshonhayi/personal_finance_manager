from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from uuid import UUID

from utils.enums import TransactionType


@dataclass(frozen=True)
class CategoryBreakdown:
    """
    Represents financial activity for a specific category.
    """
    category_id: UUID
    category_name: str
    transaction_type: TransactionType
    total_amount: Decimal
    transaction_count: int


@dataclass(frozen=True)
class FinancialReport:
    """
    Represents a calculated financial report for a specific
    date range and currency.
    """
    currency: str
    start_date: date
    end_date: date
    total_income: Decimal
    total_expense: Decimal
    transaction_count: int
    category_breakdowns: tuple[CategoryBreakdown, ...]
