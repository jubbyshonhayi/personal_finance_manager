import os

from dotenv import load_dotenv


load_dotenv()


DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")

DEBUG = os.getenv(
    "FLASK_DEBUG",
    "False"
).lower() == "true"

SESSION_COOKIE_SECURE_ENV = os.getenv("SESSION_COOKIE_SECURE")

if SESSION_COOKIE_SECURE_ENV is None:
    SESSION_COOKIE_SECURE = not DEBUG
else:
    SESSION_COOKIE_SECURE = SESSION_COOKIE_SECURE_ENV.lower() == "true"

SESSION_COOKIE_HTTPONLY = True

SESSION_COOKIE_SAMESITE = "Lax"

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

BREVO_SENDER_EMAIL = os.getenv("BREVO_SENDER_EMAIL")

BREVO_SENDER_NAME = os.getenv(
    "BREVO_SENDER_NAME",
    "Personal Finance Manager"
)

FORGOT_PASSWORD_EMAIL_LIMIT = int(
    os.getenv(
        "FORGOT_PASSWORD_EMAIL_LIMIT",
        "3"
    )
)

FORGOT_PASSWORD_IP_LIMIT = int(
    os.getenv(
        "FORGOT_PASSWORD_IP_LIMIT",
        "10"
    )
)

LOGIN_IDENTIFIER_LIMIT = int(
    os.getenv(
        "LOGIN_IDENTIFIER_LIMIT",
        "5"
    )
)

LOGIN_IP_LIMIT = int(
    os.getenv(
        "LOGIN_IP_LIMIT",
        "20"
    )
)