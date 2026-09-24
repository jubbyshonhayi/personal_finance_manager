import re

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from psycopg.errors import UniqueViolation

from database.connection import pool

from services.email_service import (
    EmailDeliveryError,
    send_password_reset_email
)

from services.password_reset_service import (
    create_password_reset_token,
    get_user_for_reset_token,
    invalidate_password_reset_token,
    reset_user_password
)

from services.subscription_service import create_free_subscription

from services.user_service import (
    create_user,
    get_user_by_email,
    get_user_by_login_identifier
)

from utils.passwords import hash_password, verify_password

from config import (
    FORGOT_PASSWORD_EMAIL_LIMIT,
    FORGOT_PASSWORD_IP_LIMIT,
    LOGIN_IDENTIFIER_LIMIT,
    LOGIN_IP_LIMIT
)

from utils.rate_limit import (
    clear_rate_limit,
    consume_rate_limit,
    get_client_ip
)


auth = Blueprint("auth", __name__)

MAX_EMAIL_LENGTH = 254
MAX_PASSWORD_LENGTH = 128
PASSWORD_RESET_TOKEN_LENGTH = 43


def _is_valid_email(email: str) -> bool:
    """
    Validates the application's accepted email format.
    """
    return (
        len(email) <= MAX_EMAIL_LENGTH
        and re.fullmatch(
            r"^[^@\s]+@[^@\s]+\.[^@\s]+$",
            email
        ) is not None
    )


def _is_valid_reset_token(token: str) -> bool:
    """
    Validates the expected format of generated reset tokens.
    """
    return (
        len(token) == PASSWORD_RESET_TOKEN_LENGTH
        and re.fullmatch(r"[A-Za-z0-9_-]+", token) is not None
    )


@auth.route("/register", methods=["GET", "POST"])
def register():
    """
    Displays the registration page and handles registration submissions.
    """
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")

        if not username or not email or not password or not confirm_password:
            flash("All fields are required.", "danger")
            return redirect(url_for("auth.register"))

        username = username.strip()
        email = email.strip().lower()

        if not username:
            flash("Username cannot be empty.", "danger")
            return redirect(url_for("auth.register"))

        if not email:
            flash("Email cannot be empty.", "danger")
            return redirect(url_for("auth.register"))

        if len(username) < 3:
            flash(
                "Username must be at least 3 characters long.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if len(username) > 30:
            flash(
                "Username must not exceed 30 characters.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if not re.fullmatch(r"[A-Za-z0-9_]+", username):
            flash(
                "Username can only contain letters, numbers, "
                "and underscores.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if len(email) > MAX_EMAIL_LENGTH:
            flash(
                "Email address is too long.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if not _is_valid_email(email):
            flash(
                "Please enter a valid email address.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters long.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if len(password) > MAX_PASSWORD_LENGTH:
            flash(
                "Password must not exceed 128 characters.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        password_hash = hash_password(password)

        try:
            with pool.connection() as connection:
                user = create_user(
                    connection=connection,
                    username=username,
                    email=email,
                    password_hash=password_hash
                )

                create_free_subscription(
                    connection=connection,
                    user_id=user.id
                )

        except UniqueViolation:
            flash(
                "Username or email already exists.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        except RuntimeError:
            flash(
                "Something went wrong while creating your account. "
                "Please try again.",
                "danger"
            )
            return redirect(url_for("auth.register"))

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """
    Displays the login page and handles login submissions.
    """
    if request.method == "POST":
        identifier = request.form.get("identifier")
        password = request.form.get("password")

        if not identifier or not password:
            flash(
                "Username/email and password are required.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        identifier = identifier.strip().lower()

        if not identifier:
            flash(
                "Username/email and password are required.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        if len(identifier) > MAX_EMAIL_LENGTH:
            flash(
                "Username/email is too long.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        if len(password) > MAX_PASSWORD_LENGTH:
            flash(
                "Password must not exceed 128 characters.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        client_ip = get_client_ip(request)

        with pool.connection() as connection:
            identifier_allowed, _ = consume_rate_limit(
                connection=connection,
                scope="login_identifier",
                identifier=identifier,
                limit=LOGIN_IDENTIFIER_LIMIT
            )

            ip_allowed, _ = consume_rate_limit(
                connection=connection,
                scope="login_ip",
                identifier=client_ip,
                limit=LOGIN_IP_LIMIT
            )

            if not identifier_allowed or not ip_allowed:
                flash(
                    "Too many login attempts. Please try again later.",
                    "warning"
                )
                return redirect(url_for("auth.login"))

            user = get_user_by_login_identifier(
                connection=connection,
                identifier=identifier
            )

            if user is None or not verify_password(
                password,
                user.password_hash
            ):
                flash(
                    "Invalid username/email or password.",
                    "danger"
                )
                return redirect(url_for("auth.login"))

            clear_rate_limit(
                connection=connection,
                scope="login_identifier",
                identifier=identifier
            )

            clear_rate_limit(
                connection=connection,
                scope="login_ip",
                identifier=client_ip
            )

            session.clear()
            session["user_id"] = str(user.id)

        flash(
            "Login successful.",
            "success"
        )

        return redirect(url_for("dashboard.dashboard_page"))

    return render_template("auth/login.html")


@auth.route("/logout", methods=["POST"])
def logout():
    """
    Logs the user out by clearing their session.
    """
    session.clear()

    flash(
        "You have been logged out.",
        "success"
    )

    return redirect(url_for("home.home_page"))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    """
    Allows a user to request a password-reset link.
    """
    if request.method == "GET":
        return render_template("auth/forgot_password.html")

    email = request.form.get("email", "").strip().lower()

    if not email:
        flash(
            "Please enter your email address.",
            "danger"
        )
        return render_template("auth/forgot_password.html")

    if len(email) > MAX_EMAIL_LENGTH:
        flash(
            "Email address is too long.",
            "danger"
        )
        return render_template("auth/forgot_password.html")

    if not _is_valid_email(email):
        flash(
            "Please enter a valid email address.",
            "danger"
        )
        return render_template("auth/forgot_password.html")

    client_ip = get_client_ip(request)

    token = None
    reset_url = None
    rate_limited = False

    with pool.connection() as connection:
        ip_allowed, _ = consume_rate_limit(
            connection=connection,
            scope="forgot_password_ip",
            identifier=client_ip,
            limit=FORGOT_PASSWORD_IP_LIMIT
        )

        email_allowed, _ = consume_rate_limit(
            connection=connection,
            scope="forgot_password_email",
            identifier=email,
            limit=FORGOT_PASSWORD_EMAIL_LIMIT
        )

        if not ip_allowed or not email_allowed:
            rate_limited = True
        else:
            user = get_user_by_email(
                connection=connection,
                email=email
            )

            if user is not None:
                token = create_password_reset_token(
                    connection=connection,
                    user=user
                )

                reset_url = url_for(
                    "auth.reset_password",
                    token=token,
                    _external=True
                )

    if rate_limited:
        flash(
            "If you recently requested a reset link, "
            "please check your inbox or try again later.",
            "info"
        )

        return redirect(url_for("auth.login"))

    if token is not None:
        try:
            send_password_reset_email(
                recipient_email=email,
                reset_url=reset_url
            )

        except EmailDeliveryError:
            current_app.logger.exception(
                "Password-reset email delivery failed."
            )

            try:
                with pool.connection() as connection:
                    invalidate_password_reset_token(
                        connection=connection,
                        token=token
                    )

            except Exception:
                current_app.logger.exception(
                    "Failed to invalidate password-reset token "
                    "after email delivery failure."
                )

    flash(
        "If an account exists for that email, "
        "a password-reset link has been sent.",
        "info"
    )

    return redirect(url_for("auth.login"))


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    """
    Allows a user to set a new password using a valid
    password-reset token.
    """
    if not _is_valid_reset_token(token):
        flash(
            "This password-reset link is invalid or has expired.",
            "danger"
        )
        return redirect(url_for("auth.login"))

    with pool.connection() as connection:
        user = get_user_for_reset_token(
            connection=connection,
            token=token
        )

        if user is None:
            flash(
                "This password-reset link is invalid or has expired.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        if request.method == "GET":
            return render_template(
                "auth/reset_password.html",
                token=token
            )

        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(password) < 8:
            flash(
                "Password must be at least 8 characters long.",
                "danger"
            )
            return render_template(
                "auth/reset_password.html",
                token=token
            )

        if len(password) > MAX_PASSWORD_LENGTH:
            flash(
                "Password must not exceed 128 characters.",
                "danger"
            )
            return render_template(
                "auth/reset_password.html",
                token=token
            )

        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return render_template(
                "auth/reset_password.html",
                token=token
            )

        password_hash = hash_password(password)

        try:
            reset_success = reset_user_password(
                connection=connection,
                token=token,
                password_hash=password_hash
            )

        except RuntimeError:
            flash(
                "Something went wrong while resetting your password. "
                "Please try again.",
                "danger"
            )
            return redirect(url_for("auth.login"))

        if not reset_success:
            flash(
                "This password-reset link is no longer valid.",
                "danger"
            )
            return redirect(url_for("auth.login"))

    session.clear()

    flash(
        "Your password has been reset successfully. "
        "You can now log in.",
        "success"
    )

    return redirect(url_for("auth.login"))
