from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID
from utils.enums import BillingInterval, SubscriptionStatus 


@dataclass(frozen=True)
class SubscriptionPlan:
    """
    Represents a subscription plan offered by the application.
    """
    id: UUID
    plan_name: str
    description: str | None
    price: Decimal
    currency: str
    billing_interval: BillingInterval
    is_active: bool


@dataclass(frozen=True)
class UserSubscription:
    """
    Represents a user's subscription to a subscription plan.
    """
    id: UUID
    user_id: UUID
    plan_id: UUID
    start_date: datetime
    end_date: datetime | None
    status: SubscriptionStatus