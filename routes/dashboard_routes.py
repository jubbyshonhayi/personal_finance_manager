from uuid import UUID

from flask import (
    Blueprint,
    render_template,
    request,
    session,
)

from database.connection import pool

from services.budget_service import (
    get_budget_progress_for_user,
)

from services.financial_service import (
    REPORTING_PERIODS,
    get_available_currencies,
    get_financial_report,
    get_reporting_period_dates,
)

from services.transaction_service import (
    get_transaction_summaries_for_user,
)

from utils.auth import login_required
from utils.enums import TransactionType


dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_page():
    """
    Displays the user's financial dashboard.

    Financial calculations are performed for the selected
    currency and reporting period, while budget progress
    always reflects the current month.
    """
    user_id = UUID(session["user_id"])

    requested_period = request.args.get(
        "period",
        "all_time"
    )

    if requested_period in REPORTING_PERIODS:
        selected_period = requested_period
    else:
        selected_period = "all_time"

    start_date, end_date = get_reporting_period_dates(
        period=selected_period
    )

    with pool.connection() as connection:
        budget_progress = get_budget_progress_for_user(
            connection=connection,
            user_id=user_id
        )

        currencies = get_available_currencies(
            connection=connection,
            user_id=user_id
        )

        recent_transactions = get_transaction_summaries_for_user(
            connection=connection,
            user_id=user_id
        )

        if not currencies:
            return render_template(
                "dashboard/dashboard.html",
                currencies=[],
                selected_currency=None,
                reporting_periods=REPORTING_PERIODS,
                selected_period=selected_period,
                summary=None,
                net_amount=None,
                category_breakdown=[],
                budget_progress=budget_progress,
                recent_transactions=recent_transactions,
                TransactionType=TransactionType
            )

        requested_currency = request.args.get("currency")

        if requested_currency in currencies:
            selected_currency = requested_currency
        else:
            selected_currency = currencies[0]

        report = get_financial_report(
            connection=connection,
            user_id=user_id,
            currency=selected_currency,
            start_date=start_date,
            end_date=end_date
        )

    net_amount = (
        report.total_income - report.total_expense
    )

    return render_template(
        "dashboard/dashboard.html",
        currencies=currencies,
        selected_currency=selected_currency,
        reporting_periods=REPORTING_PERIODS,
        selected_period=selected_period,
        summary=report,
        net_amount=net_amount,
        category_breakdown=report.category_breakdowns,
        budget_progress=budget_progress,
        recent_transactions=recent_transactions,
        TransactionType=TransactionType
    )
