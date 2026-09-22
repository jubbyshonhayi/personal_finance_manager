from decimal import Decimal
from uuid import UUID

from models.financial_summary import (
    CategoryBreakdown,
    FinancialSummary,
)
from utils.enums import TransactionType


def get_available_currencies(
    connection,
    user_id: UUID
) -> list[str]:
    """
    Retrieves the currencies used by a user's transactions.

    Returns currencies in alphabetical order.
    """
    rows = connection.execute(
        """
        SELECT DISTINCT currency
        FROM transactions
        WHERE user_id = %s
        ORDER BY currency;
        """,
        (user_id,)
    ).fetchall()

    return [row[0] for row in rows]


def get_financial_summary(
    connection,
    user_id: UUID,
    currency: str
) -> FinancialSummary:
    """
    Calculates income, expenses, and transaction count
    for a user in one specific currency.
    """
    row = connection.execute(
        """
        SELECT
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = %s
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ),
            COALESCE(
                SUM(
                    CASE
                        WHEN transaction_type = %s
                        THEN amount
                        ELSE 0
                    END
                ),
                0
            ),
            COUNT(*)
        FROM transactions
        WHERE user_id = %s
          AND currency = %s;
        """,
        (
            TransactionType.INCOME.value,
            TransactionType.EXPENSE.value,
            user_id,
            currency
        )
    ).fetchone()

    total_income = Decimal(row[0])
    total_expense = Decimal(row[1])

    return FinancialSummary(
        currency=currency,
        total_income=total_income,
        total_expense=total_expense,
        transaction_count=row[2]
    )


def get_category_breakdown(
    connection,
    user_id: UUID,
    currency: str,
    transaction_type: TransactionType = TransactionType.EXPENSE
) -> list[CategoryBreakdown]:
    """
    Calculates financial activity grouped by category
    for one specific currency and transaction type.
    """
    rows = connection.execute(
        """
        SELECT
            c.id,
            c.category_name,
            t.transaction_type,
            COALESCE(SUM(t.amount), 0),
            COUNT(*)
        FROM transactions AS t
        JOIN categories AS c
            ON c.id = t.category_id
        WHERE t.user_id = %s
          AND t.currency = %s
          AND t.transaction_type = %s
        GROUP BY
            c.id,
            c.category_name,
            t.transaction_type
        ORDER BY
            SUM(t.amount) DESC,
            c.category_name ASC;
        """,
        (
            user_id,
            currency,
            transaction_type.value
        )
    ).fetchall()

    return [
        CategoryBreakdown(
            category_id=row[0],
            category_name=row[1],
            transaction_type=TransactionType(row[2]),
            total_amount=Decimal(row[3]),
            transaction_count=row[4]
        )
        for row in rows
    ]