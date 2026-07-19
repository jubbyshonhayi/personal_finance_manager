from enum import Enum

class TransactionType(Enum):
    """
    Represents the valid transaction types supported by the application.
    """

    INCOME = "Income"
    EXPENSE = "Expense"