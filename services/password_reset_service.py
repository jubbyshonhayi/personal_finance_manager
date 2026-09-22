from datetime import datetime, timedelta, timezone

from models.user import User

from utils.password_reset import (
    generate_reset_token,
    hash_reset_token
)


RESET_TOKEN_LIFETIME = timedelta(minutes=30)


def _cleanup_password_reset_tokens(
    connection
) -> None:
    """
    Removes expired and previously used password-reset tokens.
    """
    connection.execute(
        """
        DELETE FROM password_reset_tokens
        WHERE expires_at <= CURRENT_TIMESTAMP
           OR used_at IS NOT NULL;
        """
    )


def create_password_reset_token(
    connection,
    user: User
) -> str:
    """
    Creates a one-time password-reset token for a user.

    The raw token is returned so it can be included in the
    password-reset email. Only its hash is stored in the database.
    """
    _cleanup_password_reset_tokens(connection)

    token = generate_reset_token()
    token_hash = hash_reset_token(token)

    expires_at = (
        datetime.now(timezone.utc)
        + RESET_TOKEN_LIFETIME
    )

    connection.execute(
        """
        UPDATE password_reset_tokens
        SET used_at = CURRENT_TIMESTAMP
        WHERE user_id = %s
          AND used_at IS NULL;
        """,
        (user.id,)
    )

    connection.execute(
        """
        INSERT INTO password_reset_tokens (
            user_id,
            token_hash,
            expires_at
        )
        VALUES (%s, %s, %s);
        """,
        (
            user.id,
            token_hash,
            expires_at
        )
    )

    return token


def get_user_for_reset_token(
    connection,
    token: str
) -> User | None:
    """
    Retrieves the user associated with a valid password-reset token.
    """
    token_hash = hash_reset_token(token)

    row = connection.execute(
        """
        SELECT
            u.id,
            u.username,
            u.email,
            u.password_hash,
            u.date_joined
        FROM password_reset_tokens AS prt
        JOIN users AS u
            ON u.id = prt.user_id
        WHERE prt.token_hash = %s
          AND prt.used_at IS NULL
          AND prt.expires_at > CURRENT_TIMESTAMP;
        """,
        (token_hash,)
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


def reset_user_password(
    connection,
    token: str,
    password_hash: str
) -> bool:
    """
    Consumes a valid password-reset token and updates the
    associated user's password as one atomic operation.

    Returns True when the password was successfully reset.
    Returns False when the token is invalid, expired, or already used.
    """
    token_hash = hash_reset_token(token)

    with connection.transaction():
        row = connection.execute(
            """
            UPDATE password_reset_tokens
            SET used_at = CURRENT_TIMESTAMP
            WHERE token_hash = %s
              AND used_at IS NULL
              AND expires_at > CURRENT_TIMESTAMP
            RETURNING user_id;
            """,
            (token_hash,)
        ).fetchone()

        if row is None:
            return False

        result = connection.execute(
            """
            UPDATE users
            SET password_hash = %s
            WHERE id = %s;
            """,
            (
                password_hash,
                row[0]
            )
        )

        if result.rowcount != 1:
            raise RuntimeError(
                "Password reset user could not be updated."
            )

    return True


def invalidate_password_reset_token(
    connection,
    token: str
) -> None:
    """
    Invalidates an unused password-reset token.
    """
    token_hash = hash_reset_token(token)

    connection.execute(
        """
        UPDATE password_reset_tokens
        SET used_at = CURRENT_TIMESTAMP
        WHERE token_hash = %s
          AND used_at IS NULL;
        """,
        (token_hash,)
    )