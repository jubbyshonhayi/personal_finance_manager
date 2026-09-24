from uuid import UUID

from models.transaction import Category
from utils.enums import TransactionType


def get_categories_for_user(
    connection,
    user_id: UUID,
    transaction_type: TransactionType | None = None
) -> list[Category]:
    """
    Retrieves system and user-owned categories available to a user.
    """
    if transaction_type is None:
        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                category_name,
                transaction_type
            FROM categories
            WHERE user_id IS NULL
               OR user_id = %s
            ORDER BY category_name;
            """,
            (user_id,)
        ).fetchall()
    else:
        rows = connection.execute(
            """
            SELECT
                id,
                user_id,
                category_name,
                transaction_type
            FROM categories
            WHERE (user_id IS NULL OR user_id = %s)
              AND (
                    transaction_type IS NULL
                    OR transaction_type = %s
              )
            ORDER BY category_name;
            """,
            (user_id, transaction_type.value)
        ).fetchall()

    return [
        Category(
            id=row[0],
            user_id=row[1],
            category_name=row[2],
            transaction_type=TransactionType(row[3])
        )
        for row in rows
    ]


def create_category(
    connection,
    user_id: UUID,
    category_name: str,
    transaction_type: TransactionType
) -> Category:
    """
    Creates a user-owned transaction category.

    Category names are normalized by removing leading and trailing
    whitespace. Category uniqueness is enforced by the database.
    """
    category_name = category_name.strip()

    row = connection.execute(
        """
        INSERT INTO categories (
            user_id,
            category_name,
            transaction_type
        )
        VALUES (%s, %s, %s)
        RETURNING
            id,
            user_id,
            category_name,
            transaction_type;
        """,
        (
            user_id,
            category_name,
            transaction_type.value
        )
    ).fetchone()

    return Category(
        id=row[0],
        user_id=row[1],
        category_name=row[2],
        transaction_type=TransactionType(row[3])
    )