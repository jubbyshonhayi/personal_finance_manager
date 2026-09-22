import hashlib
import secrets

def generate_reset_token() -> str:
    """
    Generates a cryptographically secure password-reset token.
    """
    return secrets.token_urlsafe(32)


def hash_reset_token(token: str) -> str:
    """
    Creates a SHA-256 hash of a password-reset token.
    """
    return hashlib.sha256(token.encode("utf-8")).hexdigest()
