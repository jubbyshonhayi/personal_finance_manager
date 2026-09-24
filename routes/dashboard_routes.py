from uuid import UUID

from flask import (
    Blueprint,
    render_template,
    request,
    session,
)

from database.connection import pool

from services.financial_service import (
    get_available_currencies,
    get_category_breakdown,
    get_financial_summary,
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

    Financial calculations are performed for the selected currency,
    while recent transactions include all currencies.
    """
    user_id = UUID(session["user_id"])

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
            return render_template(
                "dashboard/dashboard.html",
                currencies=[],
                selected_currency=None,
                summary=None,
                net_amount=None,
                category_breakdown=[],
                recent_transactions=recent_transactions,
                TransactionType=TransactionType
            )

        requested_currency = request.args.get("currency")

        if requested_currency in currencies:
            selected_currency = requested_currency
        else:
            selected_currency = currencies[0]

        summary = get_financial_summary(
            connection=connection,
            user_id=user_id,
            currency=selected_currency
        )

        category_breakdown = get_category_breakdown(
            connection=connection,
            user_id=user_id,
            currency=selected_currency,
            transaction_type=TransactionType.EXPENSE
        )

    net_amount = (
        summary.total_income - summary.total_expense
    )

    return render_template(
        "dashboard/dashboard.html",
        currencies=currencies,
        selected_currency=selected_currency,
        summary=summary,
        net_amount=net_amount,
        category_breakdown=category_breakdown,
        recent_transactions=recent_transactions,
        TransactionType=TransactionType
    )
