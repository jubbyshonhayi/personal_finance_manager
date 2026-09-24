from decimal import Decimal, DecimalException
from uuid import UUID

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from psycopg.errors import (
    ForeignKeyViolation,
    RaiseException,
    UniqueViolation,
)

from database.connection import pool
from services.budget_service import (
    create_budget,
    delete_budget,
    get_budget_for_user,
    get_budgets_for_user,
    update_budget,
)
from services.category_service import get_categories_for_user
from utils.auth import login_required
from utils.currencies import SUPPORTED_CURRENCIES
from utils.enums import TransactionType


budget = Blueprint("budget", __name__)


def _parse_budget_form() -> tuple[UUID, str, Decimal] | None:
    """
    Parses and validates common budget form values.

    Returns:
        A tuple containing category ID, currency, and monthly limit,
        or None when validation fails.
    """
    category_id = request.form.get("category_id", "").strip()
    currency = request.form.get("currency", "").strip().upper()
    monthly_limit = request.form.get("monthly_limit", "").strip()

    if not category_id or not currency or not monthly_limit:
        flash(
            "Please complete all required fields.",
            "danger"
        )
        return None

    try:
        category_id = UUID(category_id)
    except ValueError:
        flash("Invalid category.", "danger")
        return None

    if currency not in SUPPORTED_CURRENCIES:
        flash("Invalid currency.", "danger")
        return None

    try:
        monthly_limit = Decimal(monthly_limit)
    except DecimalException:
        flash(
            "Monthly limit must be a valid number.",
            "danger"
        )
        return None

    if not monthly_limit.is_finite():
        flash(
            "Monthly limit must be a valid finite number.",
            "danger"
        )
        return None

    if monthly_limit <= 0:
        flash(
            "Monthly limit must be greater than zero.",
            "danger"
        )
        return None

    if monthly_limit.as_tuple().exponent < -4:
        flash(
            "Monthly limit cannot have more than 4 decimal places.",
            "danger"
        )
        return None

    return category_id, currency, monthly_limit


def _budget_form_redirect(
    endpoint: str,
    budget_id: UUID | None = None
):
    """
    Redirects back to the relevant budget form after validation errors.
    """
    if budget_id is None:
        return redirect(url_for(endpoint))

    return redirect(
        url_for(
            endpoint,
            budget_id=budget_id
        )
    )


@budget.route("/budgets")
@login_required
def budgets_page():
    """
    Displays all budgets belonging to the authenticated user.
    """
    user_id = UUID(session["user_id"])

    with pool.connection() as connection:
        budgets = get_budgets_for_user(
            connection=connection,
            user_id=user_id
        )

    return render_template(
        "budgets/budgets.html",
        budgets=budgets,
        currencies=SUPPORTED_CURRENCIES
    )


@budget.route(
    "/budgets/add",
    methods=["GET", "POST"]
)
@login_required
def add_budget():
    """
    Displays the add-budget form and handles submissions.
    """
    user_id = UUID(session["user_id"])

    if request.method == "POST":
        values = _parse_budget_form()

        if values is None:
            return _budget_form_redirect("budget.add_budget")

        category_id, currency, monthly_limit = values

        try:
            with pool.connection() as connection:
                create_budget(
                    connection=connection,
                    user_id=user_id,
                    category_id=category_id,
                    currency=currency,
                    monthly_limit=monthly_limit
                )

        except ValueError as error:
            flash(str(error), "danger")
            return _budget_form_redirect("budget.add_budget")

        except UniqueViolation:
            flash(
                "A budget already exists for this category and currency.",
                "danger"
            )
            return _budget_form_redirect("budget.add_budget")

        except (ForeignKeyViolation, RaiseException):
            flash(
                "The selected category is no longer available.",
                "danger"
            )
            return _budget_form_redirect("budget.add_budget")

        flash(
            "Budget created successfully.",
            "success"
        )

        return redirect(
            url_for("budget.budgets_page")
        )

    with pool.connection() as connection:
        categories = get_categories_for_user(
            connection=connection,
            user_id=user_id,
            transaction_type=TransactionType.EXPENSE
        )

    return render_template(
        "budgets/add_budget.html",
        categories=categories,
        currencies=SUPPORTED_CURRENCIES
    )


@budget.route(
    "/budgets/<budget_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_budget(budget_id):
    """
    Displays and handles the budget edit form.
    """
    user_id = UUID(session["user_id"])

    try:
        budget_id = UUID(budget_id)
    except ValueError:
        flash(
            "Budget not found.",
            "danger"
        )
        return redirect(
            url_for("budget.budgets_page")
        )

    if request.method == "GET":
        with pool.connection() as connection:
            existing_budget = get_budget_for_user(
                connection=connection,
                user_id=user_id,
                budget_id=budget_id
            )

            if existing_budget is None:
                flash(
                    "Budget not found.",
                    "danger"
                )
                return redirect(
                    url_for("budget.budgets_page")
                )

            categories = get_categories_for_user(
                connection=connection,
                user_id=user_id,
                transaction_type=TransactionType.EXPENSE
            )

        return render_template(
            "budgets/edit_budget.html",
            budget=existing_budget,
            categories=categories,
            currencies=SUPPORTED_CURRENCIES
        )

    values = _parse_budget_form()

    if values is None:
        return _budget_form_redirect(
            "budget.edit_budget",
            budget_id
        )

    category_id, currency, monthly_limit = values

    try:
        with pool.connection() as connection:
            updated_budget = update_budget(
                connection=connection,
                user_id=user_id,
                budget_id=budget_id,
                category_id=category_id,
                currency=currency,
                monthly_limit=monthly_limit
            )

    except ValueError as error:
        flash(str(error), "danger")
        return _budget_form_redirect(
            "budget.edit_budget",
            budget_id
        )

    except UniqueViolation:
        flash(
            "A budget already exists for this category and currency.",
            "danger"
        )
        return _budget_form_redirect(
            "budget.edit_budget",
            budget_id
        )

    except (ForeignKeyViolation, RaiseException):
        flash(
            "The selected category is no longer available.",
            "danger"
        )
        return _budget_form_redirect(
            "budget.edit_budget",
            budget_id
        )

    if updated_budget is None:
        flash(
            "Budget not found.",
            "danger"
        )
        return redirect(
            url_for("budget.budgets_page")
        )

    flash(
        "Budget updated successfully.",
        "success"
    )

    return redirect(
        url_for("budget.budgets_page")
    )


@budget.route(
    "/budgets/<budget_id>/delete",
    methods=["GET", "POST"]
)
@login_required
def delete_budget_page(budget_id):
    """
    Displays the budget deletion confirmation page and
    handles confirmed deletion.
    """
    user_id = UUID(session["user_id"])

    try:
        budget_id = UUID(budget_id)
    except ValueError:
        flash(
            "Budget not found.",
            "danger"
        )
        return redirect(
            url_for("budget.budgets_page")
        )

    with pool.connection() as connection:
        existing_budget = get_budget_for_user(
            connection=connection,
            user_id=user_id,
            budget_id=budget_id
        )

        if existing_budget is None:
            flash(
                "Budget not found.",
                "danger"
            )
            return redirect(
                url_for("budget.budgets_page")
            )

        if request.method == "GET":
            return render_template(
                "budgets/delete_budget.html",
                budget=existing_budget
            )

        deleted = delete_budget(
            connection=connection,
            user_id=user_id,
            budget_id=budget_id
        )

    if not deleted:
        flash(
            "Budget not found.",
            "danger"
        )
        return redirect(
            url_for("budget.budgets_page")
        )

    flash(
        "Budget deleted successfully.",
        "success"
    )

    return redirect(
        url_for("budget.budgets_page")
    )
