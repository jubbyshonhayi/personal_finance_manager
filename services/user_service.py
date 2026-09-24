from models.user import User


def _row_to_user(row) -> User:
    """
    Converts a database row into a User model.
    """
    return User(
        id=row[0],
        username=row[1],
        email=row[2],
        password_hash=row[3],
        date_joined=row[4]
    )


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

    return _row_to_user(row)


def get_user_by_email(
    connection,
    email: str
) -> User | None:
    """
    Retrieves a user by email using the provided database connection.
    Returns None if the user does not exist.
    """
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

    return _row_to_user(row)


def get_user_by_login_identifier(
    connection,
    identifier: str
) -> User | None:
    """
    Retrieves a user by username or email using the provided
    database connection.

    Returns None if the user does not exist.
    """
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

    return _row_to_user(row)
