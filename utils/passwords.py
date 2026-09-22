from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(password: str) -> str:
    """
    Creates a secure password hash.
    """
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """
    Verifies a password against its stored hash.
    """
    return check_password_hash(password_hash, password)