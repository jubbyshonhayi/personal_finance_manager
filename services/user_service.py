from database.connection import pool
from models.user import User


def create_user(
    connection,
    username: str,
    email: str,
    password_hash: str
) -> User:
    """
    Creates a new user using the provided database connection.
    """
    row = connection.execute(
        """
        INSERT INTO users (
            username,
            email,
            password_hash
        )
        VALUES (%s, %s, %s)
        RETURNING id, username, email, password_hash, date_joined;
        """,
        (
            username,
            email,
            password_hash
        )
    ).fetchone()

    return User(
        id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        date_joined=row[4]
    )


def get_user_by_username(username: str) -> User | None:
    """
    Retrieves a user by username.
    Returns None if the user does not exist.
    """
    with pool.connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                username,
                email,
                password_hash,
                date_joined
            FROM users
            WHERE LOWER(username) = LOWER(%s);
            """,
            (username,)
        ).fetchone()

    if row is None:
        return None

    return User(
        id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        date_joined=row[4]
    )


def get_user_by_email(email: str) -> User | None:
    """
    Retrieves a user by email address.
    Returns None if the user does not exist.
    """
    with pool.connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                username,
                email,
                password_hash,
                date_joined
            FROM users
            WHERE LOWER(email) = LOWER(%s);
            """,
            (email,)
        ).fetchone()

    if row is None:
        return None

    return User(
        id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        date_joined=row[4]
    )


def get_user_by_login_identifier(identifier: str) -> User | None:
    """
    Retrieves a user by username or email.
    Returns None if the user does not exist.
    """
    with pool.connection() as connection:
        row = connection.execute(
            """
            SELECT
                id,
                username,
                email,
                password_hash,
                date_joined
            FROM users
            WHERE LOWER(username) = LOWER(%s)
               OR LOWER(email) = LOWER(%s);
            """,
            (
                identifier,
                identifier
            )
        ).fetchone()

    if row is None:
        return None

    return User(
        id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        date_joined=row[4]
    )