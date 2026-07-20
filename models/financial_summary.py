from dataclasses import dataclass

@dataclass(frozen=True)
class FinancialSummary:
    """
    Represents a user's financial summary.

    Stores the total income and total expenses while providing
    the current balance as a calculated property.
    """

    total_income: float
    total_expense: float

    @property
    def balance(self) -> float:
        return self.total_income - self.total_expense