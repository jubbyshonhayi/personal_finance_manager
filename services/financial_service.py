from datetime import date, timedelta
from decimal import Decimal
from uuid import UUID

from models.financial_summary import (
    CategoryBreakdown,
    FinancialReport,
)
from utils.enums import TransactionType


REPORTING_PERIODS = {
    "all_time": "All Time",
    "this_month": "This Month",
    "last_month": "Last Month",
    "this_year": "This Year",
}


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


def get_reporting_period_dates(
    period: str,
    today: date | None = None
) -> tuple[date | None, date | None]:
    """
    Converts a validated reporting-period key into its date range.

    Returns (None, None) for all-time reporting.
    """
    if period not in REPORTING_PERIODS:
        raise ValueError("Invalid reporting period.")

    current_date = today or date.today()

    if period == "all_time":
        return None, None

    if period == "this_month":
        return (
            current_date.replace(day=1),
            current_date
        )

    if period == "last_month":
        current_month_start = current_date.replace(day=1)
        last_month_end = current_month_start - timedelta(days=1)

        return (
            last_month_end.replace(day=1),
            last_month_end
        )

    # period == "this_year"
    return (
        date(current_date.year, 1, 1),
        current_date
    )


def get_financial_report(
    connection,
    user_id: UUID,
    currency: str,
    start_date: date | None = None,
    end_date: date | None = None
) -> FinancialReport:
    """
    Calculates a financial report for one user, currency,
    and optional date range.

    The report includes income, expenses, transaction count,
    and expense breakdowns by category.
    """
    date_filter = ""
    date_params = ()

    if start_date is not None and end_date is not None:
        date_filter = """
          AND transaction_date BETWEEN %s AND %s
        """
        date_params = (start_date, end_date)

    summary_row = connection.execute(
        f"""
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
            COUNT(*),
            MIN(transaction_date),
            MAX(transaction_date)
        FROM transactions
        WHERE user_id = %s
          AND currency = %s
          {date_filter};
        """,
        (
            TransactionType.INCOME.value,
            TransactionType.EXPENSE.value,
            user_id,
            currency,
            *date_params
        )
    ).fetchone()

    category_rows = connection.execute(
        f"""
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
          {date_filter.replace("transaction_date", "t.transaction_date")}
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
            TransactionType.EXPENSE.value,
            *date_params
        )
    ).fetchall()

    report_start_date = (
        start_date
        or summary_row[3]
        or date.today()
    )
    report_end_date = (
        end_date
        or summary_row[4]
        or report_start_date
    )

    category_breakdowns = tuple(
        CategoryBreakdown(
            category_id=row[0],
            category_name=row[1],
            transaction_type=TransactionType(row[2]),
            total_amount=Decimal(row[3]),
            transaction_count=row[4]
        )
        for row in category_rows
    )

    return FinancialReport(
        currency=currency,
        start_date=report_start_date,
        end_date=report_end_date,
        total_income=Decimal(summary_row[0]),
        total_expense=Decimal(summary_row[1]),
        transaction_count=summary_row[2],
        category_breakdowns=category_breakdowns
    )
