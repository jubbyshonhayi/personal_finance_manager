from dataclasses import dataclass
from datetime import datetime
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
