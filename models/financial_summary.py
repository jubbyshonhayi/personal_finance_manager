from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class FinancialSummary:
    """
    Represents a user's financial summary.

    Stores the total income and total expenses while providing
    the current balance as a calculated property.
    """

    total_income: float
    total_expense: float
    transaction_count: int
    
    @property
    def balance(self) -> float:
        return self.total_income - self.total_expense
    

@dataclass(frozen=True)
class FinancialReport(FinancialSummary):
    """
    Represents a financial report for a specific period.

    Extends the financial summary by including the reporting
    period and the total number of transactions.
    """

    period: datetime
    
