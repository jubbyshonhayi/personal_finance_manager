from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID


@dataclass
class Budget:
    """
    Represents a user's monthly spending budget.
    """
    id: UUID
    user_id: UUID
    category_id: UUID
    category_name: str
    currency: str
    monthly_limit: Decimal
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class BudgetProgress:
    """
    Represents current-month spending against a monthly budget.
    """
    budget_id: UUID
    category_id: UUID
    category_name: str
    currency: str
    monthly_limit: Decimal
    spent_amount: Decimal
    remaining_amount: Decimal
    progress_percentage: Decimal
    is_over_budget: bool
    month_start: date
    month_end: date
