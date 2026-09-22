from datetime import date
from decimal import Decimal, DecimalException
from uuid import UUID

from utils.auth import login_required
from utils.currencies import SUPPORTED_CURRENCIES
from utils.enums import TransactionType

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
from services.category_service import (
    create_category,
    get_categories_for_user,
)
from services.transaction_service import (
    DEFAULT_TRANSACTION_PAGE_SIZE,
    TRANSACTION_HISTORY_SORT_OPTIONS,
    create_transaction,
    delete_transaction,
    get_transaction_for_user,
    get_transaction_history,
    update_transaction,
)


transaction = Blueprint("transaction", __name__)


@transaction.route("/transactions")
@login_required
def transactions_page():
    """
    Displays the user's transaction history with filtering,
    sorting, searching, and pagination.
    """
    user_id = UUID(session["user_id"])

    search = request.args.get(
        "search",
        ""
    ).strip()

    transaction_type = request.args.get(
        "type",
        ""
    ).strip()

    currency = request.args.get(
        "currency",
        ""
    ).strip().upper()

    category_id = request.args.get(
        "category",
        ""
    ).strip()

    start_date = request.args.get(
        "start_date",
        ""
    ).strip()

    end_date = request.args.get(
        "end_date",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "date_desc"
    ).strip()

    page_value = request.args.get(
        "page",
        "1"
    ).strip()

    selected_transaction_type = None

    if transaction_type:
        try:
            selected_transaction_type = TransactionType(
                transaction_type
            )
        except ValueError:
            transaction_type = ""
            selected_transaction_type = None

    if currency and currency not in SUPPORTED_CURRENCIES:
        currency = ""

    selected_category_id = None

    if category_id:
        try:
            selected_category_id = UUID(category_id)
        except ValueError:
            category_id = ""
            selected_category_id = None

    selected_start_date = None

    if start_date:
        try:
            selected_start_date = date.fromisoformat(start_date)
        except ValueError:
            start_date = ""
            selected_start_date = None

    selected_end_date = None

    if end_date:
        try:
            selected_end_date = date.fromisoformat(end_date)
        except ValueError:
            end_date = ""
            selected_end_date = None

    if sort not in TRANSACTION_HISTORY_SORT_OPTIONS:
        sort = "date_desc"

    try:
        page = int(page_value)
    except ValueError:
        page = 1

    page = max(page, 1)

    with pool.connection() as connection:
        categories = get_categories_for_user(
            connection,
            user_id
        )

        transactions, total_count = get_transaction_history(
            connection=connection,
            user_id=user_id,
            search=search or None,
            transaction_type=selected_transaction_type,
            currency=currency or None,
            category_id=selected_category_id,
            start_date=selected_start_date,
            end_date=selected_end_date,
            sort=sort,
            page=page,
            per_page=DEFAULT_TRANSACTION_PAGE_SIZE
        )

    total_pages = max(
        1,
        (
            total_count + DEFAULT_TRANSACTION_PAGE_SIZE - 1
        ) // DEFAULT_TRANSACTION_PAGE_SIZE
    )

    if page > total_pages and total_count > 0:
        page = total_pages

        with pool.connection() as connection:
            transactions, total_count = get_transaction_history(
                connection=connection,
                user_id=user_id,
                search=search or None,
                transaction_type=selected_transaction_type,
                currency=currency or None,
                category_id=selected_category_id,
                start_date=selected_start_date,
                end_date=selected_end_date,
                sort=sort,
                page=page,
                per_page=DEFAULT_TRANSACTION_PAGE_SIZE
            )

    pagination = {
        "current_page": page,
        "total_pages": total_pages,
        "total_count": total_count,
        "has_previous": page > 1,
        "has_next": page < total_pages,
        "previous_page": page - 1,
        "next_page": page + 1
    }

    return render_template(
        "transactions/transactions.html",
        transactions=transactions,
        categories=categories,
        currencies=SUPPORTED_CURRENCIES,
        transaction_types=TransactionType,
        pagination=pagination,
        filters={
            "search": search,
            "transaction_type": transaction_type,
            "currency": currency,
            "category_id": category_id,
            "start_date": start_date,
            "end_date": end_date,
            "sort": sort
        }
    )


@transaction.route(
    "/transactions/add_transaction",
    methods=["GET", "POST"]
)
@login_required
def add_transaction():
    """
    Displays the add transaction form and handles submissions.
    """
    user_id = UUID(session["user_id"])

    if request.method == "POST":
        amount = request.form.get("amount")
        currency = request.form.get("currency")
        transaction_type = request.form.get("transaction_type")
        category_id = request.form.get("category_id")
        description = request.form.get("description")
        transaction_date = request.form.get("transaction_date")

        if (
            not amount
            or not currency
            or not transaction_type
            or not category_id
            or not transaction_date
        ):
            flash("Please complete all required fields.", "danger")
            return redirect(
                url_for("transaction.add_transaction")
            )

        currency = currency.strip().upper()

        if currency not in SUPPORTED_CURRENCIES:
            flash("Invalid currency.", "danger")
            return redirect(
                url_for("transaction.add_transaction")
            )

        try:
            amount = Decimal(amount)
        except DecimalException:
            flash("Amount must be a valid number.", "danger")
            return redirect(
                url_for("transaction.add_transaction")
            )

        if not amount.is_finite():
            flash(
                "Amount must be a valid finite number.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        if amount <= 0:
            flash(
                "Amount must be greater than zero.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        if amount.as_tuple().exponent < -4:
            flash(
                "Amount cannot have more than 4 decimal places.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        try:
            transaction_type = TransactionType(transaction_type)
        except ValueError:
            flash("Invalid transaction type.", "danger")
            return redirect(
                url_for("transaction.add_transaction")
            )

        try:
            category_id = UUID(category_id)
        except ValueError:
            flash("Invalid category.", "danger")
            return redirect(
                url_for("transaction.add_transaction")
            )

        description = (
            description.strip()
            if description
            else None
        )

        if description and len(description) > 500:
            flash(
                "Description must not exceed 500 characters.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        try:
            transaction_date = date.fromisoformat(
                transaction_date
            )
        except ValueError:
            flash(
                "Invalid transaction date.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        try:
            with pool.connection() as connection:
                create_transaction(
                    connection=connection,
                    user_id=user_id,
                    amount=amount,
                    currency=currency,
                    transaction_type=transaction_type,
                    category_id=category_id,
                    description=description,
                    transaction_date=transaction_date
                )

        except RaiseException as error:
            if (
                "Transaction type does not match category type"
                in str(error)
            ):
                flash(
                    "The selected category does not match "
                    "the transaction type.",
                    "danger"
                )
                return redirect(
                    url_for("transaction.add_transaction")
                )

            if (
                "Transaction cannot use another user"
                in str(error)
            ):
                flash(
                    "You cannot use that category.",
                    "danger"
                )
                return redirect(
                    url_for("transaction.add_transaction")
                )

            raise

        except ForeignKeyViolation:
            flash(
                "The selected category does not exist.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_transaction")
            )

        flash(
            "Transaction added successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard_page")
        )

    with pool.connection() as connection:
        categories = get_categories_for_user(
            connection,
            user_id
        )

    return render_template(
        "transactions/add_transaction.html",
        categories=categories,
        currencies=SUPPORTED_CURRENCIES
    )


@transaction.route(
    "/transactions/<transaction_id>/edit",
    methods=["GET", "POST"]
)
@login_required
def edit_transaction(transaction_id):
    """
    Displays and handles the transaction edit form.
    """
    user_id = UUID(session["user_id"])

    try:
        transaction_id = UUID(transaction_id)
    except ValueError:
        flash(
            "Transaction not found.",
            "danger"
        )
        return redirect(
            url_for("dashboard.dashboard_page")
        )

    with pool.connection() as connection:
        existing_transaction = get_transaction_for_user(
            connection=connection,
            user_id=user_id,
            transaction_id=transaction_id
        )

        if existing_transaction is None:
            flash(
                "Transaction not found.",
                "danger"
            )
            return redirect(
                url_for("dashboard.dashboard_page")
            )

        if request.method == "GET":
            categories = get_categories_for_user(
                connection,
                user_id
            )

            return render_template(
                "transactions/edit_transaction.html",
                transaction=existing_transaction,
                categories=categories,
                currencies=SUPPORTED_CURRENCIES
            )

        amount = request.form.get("amount")
        currency = request.form.get("currency")
        transaction_type = request.form.get("transaction_type")
        category_id = request.form.get("category_id")
        description = request.form.get("description")
        transaction_date = request.form.get("transaction_date")

        if (
            not amount
            or not currency
            or not transaction_type
            or not category_id
            or not transaction_date
        ):
            flash(
                "Please complete all required fields.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        currency = currency.strip().upper()

        if currency not in SUPPORTED_CURRENCIES:
            flash(
                "Invalid currency.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:
            amount = Decimal(amount)
        except DecimalException:
            flash(
                "Amount must be a valid number.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        if not amount.is_finite():
            flash(
                "Amount must be a valid finite number.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        if amount <= 0:
            flash(
                "Amount must be greater than zero.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        if amount.as_tuple().exponent < -4:
            flash(
                "Amount cannot have more than 4 decimal places.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:
            transaction_type = TransactionType(
                transaction_type
            )
        except ValueError:
            flash(
                "Invalid transaction type.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:
            category_id = UUID(category_id)
        except ValueError:
            flash(
                "Invalid category.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        description = (
            description.strip()
            if description
            else None
        )

        if description and len(description) > 500:
            flash(
                "Description must not exceed 500 characters.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:
            transaction_date = date.fromisoformat(
                transaction_date
            )
        except ValueError:
            flash(
                "Invalid transaction date.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        try:
            updated_transaction = update_transaction(
                connection=connection,
                user_id=user_id,
                transaction_id=transaction_id,
                amount=amount,
                currency=currency,
                transaction_type=transaction_type,
                category_id=category_id,
                description=description,
                transaction_date=transaction_date
            )

        except RaiseException as error:
            if (
                "Transaction type does not match category type"
                in str(error)
            ):
                flash(
                    "The selected category does not match "
                    "the transaction type.",
                    "danger"
                )
                return redirect(
                    url_for(
                        "transaction.edit_transaction",
                        transaction_id=transaction_id
                    )
                )

            if (
                "Transaction cannot use another user"
                in str(error)
            ):
                flash(
                    "You cannot use that category.",
                    "danger"
                )
                return redirect(
                    url_for(
                        "transaction.edit_transaction",
                        transaction_id=transaction_id
                    )
                )

            raise

        except ForeignKeyViolation:
            flash(
                "The selected category does not exist.",
                "danger"
            )
            return redirect(
                url_for(
                    "transaction.edit_transaction",
                    transaction_id=transaction_id
                )
            )

        if updated_transaction is None:
            flash(
                "Transaction not found.",
                "danger"
            )
            return redirect(
                url_for("dashboard.dashboard_page")
            )

        flash(
            "Transaction updated successfully.",
            "success"
        )

        return redirect(
            url_for("dashboard.dashboard_page")
        )


@transaction.route(
    "/transactions/<transaction_id>/delete",
    methods=["GET", "POST"]
)
@login_required
def delete_transaction_page(transaction_id):
    """
    Displays the transaction deletion confirmation page and
    handles confirmed deletion.
    """
    user_id = UUID(session["user_id"])

    try:
        transaction_id = UUID(transaction_id)
    except ValueError:
        flash(
            "Transaction not found.",
            "danger"
        )
        return redirect(
            url_for("dashboard.dashboard_page")
        )

    with pool.connection() as connection:
        existing_transaction = get_transaction_for_user(
            connection=connection,
            user_id=user_id,
            transaction_id=transaction_id
        )

        if existing_transaction is None:
            flash(
                "Transaction not found.",
                "danger"
            )
            return redirect(
                url_for("dashboard.dashboard_page")
            )

        if request.method == "GET":
            return render_template(
                "transactions/delete_transaction.html",
                transaction=existing_transaction
            )

        deleted = delete_transaction(
            connection=connection,
            user_id=user_id,
            transaction_id=transaction_id
        )

    if not deleted:
        flash(
            "Transaction not found.",
            "danger"
        )
        return redirect(
            url_for("dashboard.dashboard_page")
        )

    flash(
        "Transaction deleted successfully.",
        "success"
    )

    return redirect(
        url_for("dashboard.dashboard_page")
    )


@transaction.route(
    "/categories/add",
    methods=["GET", "POST"]
)
@login_required
def add_category():
    """
    Displays the add category form and handles submissions.
    """
    user_id = UUID(session["user_id"])

    if request.method == "POST":
        category_name = request.form.get("category_name")
        transaction_type = request.form.get("transaction_type")

        if not category_name or not transaction_type:
            flash(
                "All fields are required.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_category")
            )

        category_name = category_name.strip()

        if not category_name:
            flash(
                "Category name cannot be empty.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_category")
            )

        if len(category_name) > 100:
            flash(
                "Category name must not exceed 100 characters.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_category")
            )

        try:
            transaction_type = TransactionType(
                transaction_type
            )
        except ValueError:
            flash(
                "Invalid transaction type.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_category")
            )

        try:
            with pool.connection() as connection:
                create_category(
                    connection=connection,
                    user_id=user_id,
                    category_name=category_name,
                    transaction_type=transaction_type
                )

        except UniqueViolation:
            flash(
                "You already have a category with this name and type.",
                "danger"
            )
            return redirect(
                url_for("transaction.add_category")
            )

        flash(
            "Category created successfully.",
            "success"
        )

        return redirect(
            url_for("transaction.add_transaction")
        )

    return render_template(
        "transactions/add_category.html"
    )