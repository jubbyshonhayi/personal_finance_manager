from enum import Enum

class TransactionType(Enum):
    """
    Represents the valid transaction types supported by the application.
    """

    INCOME = "Income"
    EXPENSE = "Expense"

class BillingInterval(Enum):
    """
    Defines the available billing intervals for subscription plans.
    """
    MONTHLY = "monthly"
    YEARLY = "yearly"

class SubscriptionStatus(Enum):
    """
    Defines the possible states of a user subscription.
    """
    ACTIVE = "active"
    CANCELLED = "cancelled"
    EXPIRED = "expired"
    SUSPENDED = "suspended"