from functools import wraps
from uuid import UUID

from flask import redirect, session, url_for


def login_required(view):
    """
    Requires a valid authenticated user session before allowing
    access to a protected route.
    """
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user_id = session.get("user_id")

        if not user_id:
            return redirect(url_for("auth.login"))

        try:
            UUID(user_id)
        except (ValueError, AttributeError, TypeError):
            session.clear()
            return redirect(url_for("auth.login"))

        return view(*args, **kwargs)

    return wrapped_view