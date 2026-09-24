import logging

from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect

from config import (
    DEBUG,
    SECRET_KEY,
    SESSION_COOKIE_SECURE
)

from routes.auth_routes import auth
from routes.budget_routes import budget
from routes.dashboard_routes import dashboard
from routes.home_routes import home
from routes.transaction_routes import transaction


if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not configured")


app = Flask(
    __name__,
    static_folder="public",
    static_url_path="/static"
)

app.config["SECRET_KEY"] = SECRET_KEY

# Session cookie security settings.
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = SESSION_COOKIE_SECURE

# Enables CSRF protection for state-changing requests such as POST.
csrf = CSRFProtect(app)


# Security headers
@app.after_request
def apply_security_headers(response):
    """
    Applies security-related HTTP response headers.
    """
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=()"
    )

    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; "
        "base-uri 'self'; "
        "connect-src 'self'; "
        "font-src 'self'; "
        "form-action 'self'; "
        "frame-ancestors 'none'; "
        "frame-src 'none'; "
        "img-src 'self'; "
        "object-src 'none'; "
        "script-src 'self'; "
        "style-src 'self';"
    )

    if SESSION_COOKIE_SECURE:
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )

    return response


# Logging
logging.basicConfig(
    level=logging.ERROR,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger(__name__)


# Error handling
@app.errorhandler(404)
def page_not_found(error):
    """
    Handles requests for routes that do not exist.
    """
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def internal_server_error(error):
    """
    Handles unexpected application errors.
    """
    logger.error(
        "Unhandled application error",
        exc_info=True
    )

    return render_template("errors/500.html"), 500


# Blueprint registrations
app.register_blueprint(home)
app.register_blueprint(auth)
app.register_blueprint(dashboard)
app.register_blueprint(transaction)
app.register_blueprint(budget)


if __name__ == "__main__":
    app.run(debug=DEBUG)
