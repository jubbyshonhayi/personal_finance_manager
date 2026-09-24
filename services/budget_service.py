from calendar import monthrange
from datetime import date
from decimal import Decimal
from uuid import UUID

from models.budget import Budget, BudgetProgress
from utils.currencies import SUPPORTED_CURRENCIES
from utils.enums import TransactionType


def _get_expense_category(
    connection,
    user_id: UUID,
    category_id: UUID
) -> tuple[UUID, str] | None:
    """
    Retrieves an expense category available to the user.

    A category is available when it is either system-owned or
    owned by the same user.
    """
    row = connection.execute(
        """
        SELECT
            id,
            category_name
        FROM categories
        WHERE id = %s
          AND (user_id IS NULL OR user_id = %s)
          AND transaction_type = %s;
        """,
        (
            category_id,
            user_id,
            TransactionType.EXPENSE.value
        )
    ).fetchone()

    if row is None:
        return None

    return row[0], row[1]


def _validate_budget_values(
    currency: str,
    monthly_limit: Decimal
) -> None:
    """
    Validates budget values before they reach the database.
    """
    if currency not in SUPPORTED_CURRENCIES:
        raise ValueError("Unsupported currency.")

    if monthly_limit <= 0:
        raise ValueError("Monthly budget limit must be greater than zero.")


def _row_to_budget(row) -> Budget:
    """
    Converts a database row into a Budget model.
    """
    return Budget(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        category_name=row[3],
        currency=row[4],
        monthly_limit=Decimal(row[5]),
        created_at=row[6],
        updated_at=row[7]
    )


def _current_month_range(
    today: date | None = None
) -> tuple[date, date]:
    """
    Returns the inclusive start and exclusive end of the current month.
    """
    current_date = today or date.today()
    month_start = current_date.replace(day=1)

    if current_date.month == 12:
        next_month_start = date(
            current_date.year + 1,
            1,
            1
        )
    else:
        next_month_start = date(
            current_date.year,
            current_date.month + 1,
            1
        )

    return month_start, next_month_start


def _row_to_budget_progress(
    row,
    month_start: date,
    month_end: date
) -> BudgetProgress:
    """
    Converts a database row into a BudgetProgress model.
    """
    monthly_limit = Decimal(row[4])
    spent_amount = Decimal(row[5])
    remaining_amount = monthly_limit - spent_amount

    if monthly_limit > 0:
        progress_percentage = (
            spent_amount / monthly_limit
        ) * Decimal("100")
    else:
        progress_percentage = Decimal("0")

    return BudgetProgress(
        budget_id=row[0],
        category_id=row[2],
        category_name=row[3],
        currency=row[4],
        monthly_limit=monthly_limit,
        spent_amount=spent_amount,
        remaining_amount=remaining_amount,
        progress_percentage=progress_percentage,
        is_over_budget=spent_amount > monthly_limit,
        month_start=month_start,
        month_end=month_end
    )


def create_budget(
    connection,
    user_id: UUID,
    category_id: UUID,
    currency: str,
    monthly_limit: Decimal
) -> Budget:
    """
    Creates a monthly budget for an expense category.

    Database constraints remain the final integrity authority,
    including the unique user/category/currency constraint.
    """
    _validate_budget_values(
        currency=currency,
        monthly_limit=monthly_limit
    )

    category = _get_expense_category(
        connection=connection,
        user_id=user_id,
        category_id=category_id
    )

    if category is None:
        raise ValueError("Invalid or inaccessible expense category.")

    row = connection.execute(
        """
        INSERT INTO budgets (
            user_id,
            category_id,
            currency,
            monthly_limit
        )
        VALUES (%s, %s, %s, %s)
        RETURNING
            id,
            user_id,
            category_id,
            currency,
            monthly_limit,
            created_at,
            updated_at;
        """,
        (
            user_id,
            category_id,
            currency,
            monthly_limit
        )
    ).fetchone()

    return Budget(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        category_name=category[1],
        currency=row[3],
        monthly_limit=Decimal(row[4]),
        created_at=row[5],
        updated_at=row[6]
    )


def get_budget_for_user(
    connection,
    user_id: UUID,
    budget_id: UUID
) -> Budget | None:
    """
    Retrieves a specific budget belonging to a user.
    """
    row = connection.execute(
        """
        SELECT
            b.id,
            b.user_id,
            b.category_id,
            c.category_name,
            b.currency,
            b.monthly_limit,
            b.created_at,
            b.updated_at
        FROM budgets AS b
        JOIN categories AS c
            ON c.id = b.category_id
        WHERE b.id = %s
          AND b.user_id = %s;
        """,
        (budget_id, user_id)
    ).fetchone()

    if row is None:
        return None

    return _row_to_budget(row)


def get_budgets_for_user(
    connection,
    user_id: UUID
) -> list[Budget]:
    """
    Retrieves all budgets belonging to a user.

    Budgets are ordered by category name and currency for
    predictable display and processing.
    """
    rows = connection.execute(
        """
        SELECT
            b.id,
            b.user_id,
            b.category_id,
            c.category_name,
            b.currency,
            b.monthly_limit,
            b.created_at,
            b.updated_at
        FROM budgets AS b
        JOIN categories AS c
            ON c.id = b.category_id
        WHERE b.user_id = %s
        ORDER BY
            c.category_name ASC,
            b.currency ASC,
            b.id ASC;
        """,
        (user_id,)
    ).fetchall()

    return [_row_to_budget(row) for row in rows]


def get_budget_progress_for_user(
    connection,
    user_id: UUID,
    today: date | None = None
) -> list[BudgetProgress]:
    """
    Calculates current-month spending against every user budget.

    Budgets with no matching transactions are included with zero
    spending. Transaction aggregation is performed by PostgreSQL.
    """
    month_start, month_end = _current_month_range(today)

    rows = connection.execute(
        """
        SELECT
            b.id,
            b.user_id,
            b.category_id,
            c.category_name,
            b.monthly_limit,
            COALESCE(SUM(t.amount), 0),
            b.currency
        FROM budgets AS b
        JOIN categories AS c
            ON c.id = b.category_id
        LEFT JOIN transactions AS t
            ON t.user_id = b.user_id
           AND t.category_id = b.category_id
           AND t.currency = b.currency
           AND t.transaction_type = %s
           AND t.transaction_date >= %s
           AND t.transaction_date < %s
        WHERE b.user_id = %s
        GROUP BY
            b.id,
            b.user_id,
            b.category_id,
            c.category_name,
            b.monthly_limit,
            b.currency
        ORDER BY
            b.currency ASC,
            c.category_name ASC,
            b.id ASC;
        """,
        (
            TransactionType.EXPENSE.value,
            month_start,
            month_end,
            user_id
        )
    ).fetchall()

    return [
        _row_to_budget_progress(
            row=row,
            month_start=month_start,
            month_end=month_end
        )
        for row in rows
    ]


def update_budget(
    connection,
    user_id: UUID,
    budget_id: UUID,
    category_id: UUID,
    currency: str,
    monthly_limit: Decimal
) -> Budget | None:
    """
    Updates a budget belonging to a user.

    Returns None when the budget does not exist for the user.
    """
    _validate_budget_values(
        currency=currency,
        monthly_limit=monthly_limit
    )

    category = _get_expense_category(
        connection=connection,
        user_id=user_id,
        category_id=category_id
    )

    if category is None:
        raise ValueError("Invalid or inaccessible expense category.")

    row = connection.execute(
        """
        UPDATE budgets
        SET
            category_id = %s,
            currency = %s,
            monthly_limit = %s,
            updated_at = CURRENT_TIMESTAMP
        WHERE id = %s
          AND user_id = %s
        RETURNING
            id,
            user_id,
            category_id,
            currency,
            monthly_limit,
            created_at,
            updated_at;
        """,
        (
            category_id,
            currency,
            monthly_limit,
            budget_id,
            user_id
        )
    ).fetchone()

    if row is None:
        return None

    return Budget(
        id=row[0],
        user_id=row[1],
        category_id=row[2],
        category_name=category[1],
        currency=row[3],
        monthly_limit=Decimal(row[4]),
        created_at=row[5],
        updated_at=row[6]
    )


def delete_budget(
    connection,
    user_id: UUID,
    budget_id: UUID
) -> bool:
    """
    Deletes a budget belonging to a user.

    Returns True when a budget was deleted, otherwise False.
    """
    result = connection.execute(
        """
        DELETE FROM budgets
        WHERE id = %s
          AND user_id = %s;
        """,
        (budget_id, user_id)
    )

    return result.rowcount == 1
