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
dashboard = Blueprint("dashboard", __name__)


@dashboard.route("/dashboard")
@login_required
def dashboard_page():
    """
    Displays the user's financial dashboard.

    Financial calculations are performed for the selected
    currency and reporting period. The selected currency is
    persisted in the session so navigation between pages does
    not reset the user's dashboard context.

    Budget progress always reflects the current month and the
    selected dashboard currency.
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
        currencies = get_available_currencies(
            connection=connection,
            user_id=user_id
        )

        recent_transactions = get_transaction_summaries_for_user(
            connection=connection,
            user_id=user_id
        )

        if not currencies:
            session.pop("dashboard_currency", None)

            return render_template(
                "dashboard/dashboard.html",
                currencies=[],
                selected_currency=None,
                reporting_periods=REPORTING_PERIODS,
                selected_period=selected_period,
                summary=None,
                net_amount=None,
                category_breakdown=[],
                budget_progress=[],
                recent_transactions=recent_transactions
            )

        requested_currency = request.args.get("currency")
        session_currency = session.get("dashboard_currency")

        if requested_currency in currencies:
            selected_currency = requested_currency
        elif session_currency in currencies:
            selected_currency = session_currency
        else:
            selected_currency = currencies[0]

        session["dashboard_currency"] = selected_currency

        report = get_financial_report(
            connection=connection,
            user_id=user_id,
            currency=selected_currency,
            start_date=start_date,
            end_date=end_date
        )

        budget_progress = get_budget_progress_for_user(
            connection=connection,
            user_id=user_id,
            currency=selected_currency
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
        recent_transactions=recent_transactions
    )
