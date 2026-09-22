import html

from brevo import Brevo
from brevo.core.api_error import ApiError
from brevo.transactional_emails import (
    SendTransacEmailRequestSender,
    SendTransacEmailRequestToItem
)

from config import (
    BREVO_API_KEY,
    BREVO_SENDER_EMAIL,
    BREVO_SENDER_NAME
)


class EmailDeliveryError(RuntimeError):
    """
    Represents a failure while sending an application email.
    """


def _get_brevo_client() -> Brevo:
    """
    Creates a Brevo API client using the configured API key.
    """
    if not BREVO_API_KEY:
        raise EmailDeliveryError(
            "Brevo API key is not configured."
        )

    return Brevo(
        api_key=BREVO_API_KEY,
        timeout=10.0
    )


def send_password_reset_email(
    recipient_email: str,
    reset_url: str
) -> str:
    """
    Sends a password-reset email to a user.

    Returns the Brevo message ID when the email is accepted.
    """
    if not recipient_email:
        raise EmailDeliveryError(
            "Password reset recipient email is missing."
        )

    if not reset_url:
        raise EmailDeliveryError(
            "Password reset URL is missing."
        )

    if not BREVO_SENDER_EMAIL:
        raise EmailDeliveryError(
            "Brevo sender email is not configured."
        )

    sender_name = (
        BREVO_SENDER_NAME
        or "Personal Finance Manager"
    )

    safe_reset_url = html.escape(
        reset_url,
        quote=True
    )

    html_content = f"""
    <html>
        <body>
            <p>Hello,</p>

            <p>
                We received a request to reset the password
                for your Personal Finance Manager account.
            </p>

            <p>
                <a href="{safe_reset_url}">
                    Reset your password
                </a>
            </p>

            <p>
                This link will expire in 30 minutes.
            </p>

            <p>
                If you did not request a password reset,
                you can safely ignore this email.
            </p>

            <p>
                Personal Finance Manager
            </p>
        </body>
    </html>
    """

    client = _get_brevo_client()

    try:
        result = client.transactional_emails.send_transac_email(
            subject="Reset your Personal Finance Manager password",
            html_content=html_content,
            sender=SendTransacEmailRequestSender(
                name=sender_name,
                email=BREVO_SENDER_EMAIL
            ),
            to=[
                SendTransacEmailRequestToItem(
                    email=recipient_email
                )
            ],
            request_options={
                "timeout_in_seconds": 10,
                "max_retries": 2
            }
        )

    except ApiError as exc:
        raise EmailDeliveryError(
            "Brevo could not send the password-reset email."
        ) from exc

    return result.message_id