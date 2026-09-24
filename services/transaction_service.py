from datetime import date
from decimal import Decimal
from uuid import UUID

from models.transaction import Transaction, TransactionSummary
from utils.enums import TransactionType


TRANSACTION_HISTORY_SORT_OPTIONS = {
    "date_desc": "t.transaction_date DESC, t.id DESC",
    "date_asc": "t.transaction_date ASC, t.id ASC",
    "amount_desc": "t.amount DESC, t.id DESC",
    "amount_asc": "t.amount ASC, t.id ASC",
    "category_asc": (
        "c.category_name ASC, "
        "t.transaction_date DESC, "
        "t.id DESC"
    ),
    "category_desc": (
        "c.category_name DESC, "
        "t.transaction_date DESC, "
        "t.id DESC"
    )
}

DEFAULT_TRANSACTION_PAGE_SIZE = 10
MAX_TRANSACTION_PAGE_SIZE = 10


def create_transaction(
    connection,
    user_id: UUID,
    amount: Decimal,
    currency: str,
    transaction_type: TransactionType,
    category_id: UUID,
    description: str | None,
    transaction_date: date
) -> Transaction:
    """
    Creates a transaction for a user using the provided
    database connection.

    Database constraints and triggers provide the final
    integrity and authorization checks.
    """
    row = connection.execute(
        """
        INSERT INTO transactions (
            user_id,
            amount,
            currency,
            transaction_type,
            category_id,
            description,
            transaction_date
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        RETURNING
            id,
            user_id,
            amount,
            currency,
            transaction_type,
            category_id,
            description,
            transaction_date;
        """,
        (
            user_id,
            amount,
            currency,
            transaction_type.value,
            category_id,
            description,
            transaction_date
        )
    ).fetchone()

    return Transaction(
        id=row[0],
        user_id=row[1],
        amount=row[2],
        currency=row[3],
        transaction_type=TransactionType(row[4]),
        category_id=row[5],
        description=row[6],
        transaction_date=row[7]
    )


def get_transaction_for_user(
    connection,
    user_id: UUID,
    transaction_id: UUID
) -> Transaction | None:
    """
    Retrieves a specific transaction belonging to a user.

    Returns None if the transaction does not exist for the user.
    """
    row = connection.execute(
        """
        SELECT
            id,
            user_id,
            amount,
            currency,
            transaction_type,
            category_id,
            description,
            transaction_date
        FROM transactions
        WHERE id = %s
          AND user_id = %s;
        """,
        (transaction_id, user_id)
    ).fetchone()

    if row is None:
        return None

    return Transaction(
        id=row[0],
        user_id=row[1],
        amount=row[2],
        currency=row[3],
        transaction_type=TransactionType(row[4]),
        category_id=row[5],
        description=row[6],
        transaction_date=row[7]
    )


def get_transactions_for_user(
    connection,
    user_id: UUID
) -> list[Transaction]:
    """
    Retrieves all transactions belonging to a user.

    Transactions are returned from newest to oldest.
    """
    rows = connection.execute(
        """
        SELECT
            id,
            user_id,
            amount,
            currency,
            transaction_type,
            category_id,
            description,
            transaction_date
        FROM transactions
        WHERE user_id = %s
        ORDER BY transaction_date DESC, id DESC;
        """,
        (user_id,)
    ).fetchall()

    return [
        Transaction(
            id=row[0],
            user_id=row[1],
            amount=row[2],
            currency=row[3],
            transaction_type=TransactionType(row[4]),
            category_id=row[5],
            description=row[6],
            transaction_date=row[7]
        )
        for row in rows
    ]


def get_transaction_history(
    connection,
    user_id: UUID,
    search: str | None = None,
    transaction_type: TransactionType | None = None,
    currency: str | None = None,
    category_id: UUID | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    sort: str = "date_desc",
    page: int = 1,
    per_page: int = DEFAULT_TRANSACTION_PAGE_SIZE
) -> tuple[list[TransactionSummary], int]:
    """
    Retrieves a paginated transaction history for a user.

    Supports searching, filtering, sorting, and pagination.

    Returns:
        A tuple containing:
        - the transactions for the requested page
        - the total number of transactions matching the filters
    """
    page = max(page, 1)

    per_page = min(
        max(per_page, 1),
        MAX_TRANSACTION_PAGE_SIZE
    )

    order_by = TRANSACTION_HISTORY_SORT_OPTIONS.get(
        sort,
        TRANSACTION_HISTORY_SORT_OPTIONS["date_desc"]
    )

    conditions = [
        "t.user_id = %s"
    ]

    parameters = [user_id]

    if search:
        search_pattern = f"%{search.strip()}%"

        conditions.append(
            """
            (
                t.description ILIKE %s
                OR c.category_name ILIKE %s
            )
            """
        )

        parameters.extend([
            search_pattern,
            search_pattern
        ])

    if transaction_type is not None:
        conditions.append(
            "t.transaction_type = %s"
        )

        parameters.append(transaction_type.value)

    if currency:
        conditions.append(
            "t.currency = %s"
        )

        parameters.append(currency)

    if category_id is not None:
        conditions.append(
            "t.category_id = %s"
        )

        parameters.append(category_id)

    if start_date is not None:
        conditions.append(
            "t.transaction_date >= %s"
        )

        parameters.append(start_date)

    if end_date is not None:
        conditions.append(
            "t.transaction_date <= %s"
        )

        parameters.append(end_date)

    where_clause = " AND ".join(conditions)

    count_row = connection.execute(
        f"""
        SELECT COUNT(*)
        FROM transactions AS t
        JOIN categories AS c
            ON c.id = t.category_id
        WHERE {where_clause};
        """,
        parameters
    ).fetchone()

    total_count = count_row[0]

    offset = (page - 1) * per_page

    rows = connection.execute(
        f"""
        SELECT
            t.id,
            t.user_id,
            t.amount,
            t.currency,
            t.transaction_type,
            t.category_id,
            c.category_name,
            t.description,
            t.transaction_date
        FROM transactions AS t
        JOIN categories AS c
            ON c.id = t.category_id
        WHERE {where_clause}
        ORDER BY {order_by}
        LIMIT %s
        OFFSET %s;
        """,
        parameters + [per_page, offset]
    ).fetchall()

    transactions = [
        TransactionSummary(
            id=row[0],
            user_id=row[1],
            amount=row[2],
            currency=row[3],
            transaction_type=TransactionType(row[4]),
            category_id=row[5],
            category_name=row[6],
            description=row[7] if row[7] else None,
            transaction_date=row[8]
        )
        for row in rows
    ]

    return transactions, total_count


def get_transaction_summaries_for_user(
    connection,
    user_id: UUID
) -> list[TransactionSummary]:
    """
    Retrieves the five most recent transactions for the dashboard.

    Unlike the paginated transaction history, this query does not
    need a separate count query.
    """
    rows = connection.execute(
        """
        SELECT
            t.id,
            t.user_id,
            t.amount,
            t.currency,
            t.transaction_type,
            t.category_id,
            c.category_name,
            t.description,
            t.transaction_date
        FROM transactions AS t
        JOIN categories AS c
            ON c.id = t.category_id
        WHERE t.user_id = %s
        ORDER BY
            t.transaction_date DESC,
            t.id DESC
        LIMIT 5;
        """,
        (user_id,)
    ).fetchall()

    return [
        TransactionSummary(
            id=row[0],
            user_id=row[1],
            amount=row[2],
            currency=row[3],
            transaction_type=TransactionType(row[4]),
            category_id=row[5],
            category_name=row[6],
            description=row[7] if row[7] else None,
            transaction_date=row[8]
        )
        for row in rows
    ]


def update_transaction(
    connection,
    user_id: UUID,
    transaction_id: UUID,
    amount: Decimal,
    currency: str,
    transaction_type: TransactionType,
    category_id: UUID,
    description: str | None,
    transaction_date: date
) -> Transaction | None:
    """
    Updates a transaction belonging to a specific user.

    Returns the updated transaction, or None if the transaction
    does not exist for the given user.

    Database constraints and triggers provide the final
    integrity and authorization checks.
    """
    row = connection.execute(
        """
        UPDATE transactions
        SET
            amount = %s,
            currency = %s,
            transaction_type = %s,
            category_id = %s,
            description = %s,
            transaction_date = %s
        WHERE id = %s
          AND user_id = %s
        RETURNING
            id,
            user_id,
            amount,
            currency,
            transaction_type,
            category_id,
            description,
            transaction_date;
        """,
        (
            amount,
            currency,
            transaction_type.value,
            category_id,
            description,
            transaction_date,
            transaction_id,
            user_id
        )
    ).fetchone()

    if row is None:
        return None

    return Transaction(
        id=row[0],
        user_id=row[1],
        amount=row[2],
        currency=row[3],
        transaction_type=TransactionType(row[4]),
        category_id=row[5],
        description=row[6],
        transaction_date=row[7]
    )


def delete_transaction(
    connection,
    user_id: UUID,
    transaction_id: UUID
) -> bool:
    """
    Deletes a transaction belonging to a specific user.

    Returns True if a transaction was deleted, otherwise False.
    """
    result = connection.execute(
        """
        DELETE FROM transactions
        WHERE id = %s
          AND user_id = %s;
        """,
        (transaction_id, user_id)
    )

    return result.rowcount == 1
