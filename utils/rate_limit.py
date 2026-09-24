import hashlib
import hmac
import os
from datetime import datetime, timedelta, timezone

from config import SECRET_KEY


RATE_LIMIT_WINDOW = timedelta(minutes=15)


def _hash_rate_limit_key(
    scope: str,
    identifier: str
) -> str:
    """
    Creates a privacy-preserving key for a rate-limit bucket.
    """
    if not SECRET_KEY:
        raise RuntimeError("SECRET_KEY is not configured")

    value = f"{scope}:{identifier}".encode("utf-8")

    return hmac.new(
        SECRET_KEY.encode("utf-8"),
        value,
        hashlib.sha256
    ).hexdigest()


def _get_window_start(
    current_time: datetime
) -> datetime:
    """
    Returns the start of the current fixed-rate-limit window.
    """
    timestamp = int(current_time.timestamp())

    window_seconds = int(
        RATE_LIMIT_WINDOW.total_seconds()
    )

    window_timestamp = (
        timestamp
        - (timestamp % window_seconds)
    )

    return datetime.fromtimestamp(
        window_timestamp,
        tz=timezone.utc
    )


def _cleanup_expired_buckets(
    connection,
    current_window_start: datetime
) -> None:
    """
    Removes rate-limit buckets from previous windows.
    """
    connection.execute(
        """
        DELETE FROM auth_rate_limit_buckets
        WHERE window_started_at < %s;
        """,
        (current_window_start,)
    )


def get_client_ip(request) -> str:
    """
    Retrieves the client IP address using the appropriate
    source for the current deployment environment.
    """
    if os.getenv("VERCEL") == "1":
        client_ip = request.headers.get(
            "x-vercel-forwarded-for"
        )

        if client_ip:
            return client_ip.strip()

        client_ip = request.headers.get("x-real-ip")

        if client_ip:
            return client_ip.strip()

    return request.remote_addr or "unknown"


def consume_rate_limit(
    connection,
    scope: str,
    identifier: str,
    limit: int
) -> tuple[bool, int]:
    """
    Records one request and checks whether it is within
    the configured rate limit.

    This uses a single atomic PostgreSQL upsert so concurrent
    requests cannot bypass the request counter.
    """
    current_time = datetime.now(timezone.utc)

    window_start = _get_window_start(
        current_time
    )

    _cleanup_expired_buckets(
        connection=connection,
        current_window_start=window_start
    )

    bucket_key = _hash_rate_limit_key(
        scope=scope,
        identifier=identifier
    )

    row = connection.execute(
        """
        INSERT INTO auth_rate_limit_buckets (
            bucket_key,
            window_started_at,
            request_count
        )
        VALUES (%s, %s, 1)
        ON CONFLICT (
            bucket_key,
            window_started_at
        )
        DO UPDATE SET
            request_count =
                auth_rate_limit_buckets.request_count + 1
        RETURNING request_count;
        """,
        (
            bucket_key,
            window_start
        )
    ).fetchone()

    request_count = row[0]

    window_end = (
        window_start
        + RATE_LIMIT_WINDOW
    )

    retry_after = max(
        0,
        int(
            (
                window_end - current_time
            ).total_seconds()
        )
    )

    return request_count <= limit, retry_after


def clear_rate_limit(
    connection,
    scope: str,
    identifier: str
) -> None:
    """
    Clears the current rate-limit bucket for an identifier.
    """
    current_time = datetime.now(timezone.utc)

    window_start = _get_window_start(
        current_time
    )

    bucket_key = _hash_rate_limit_key(
        scope=scope,
        identifier=identifier
    )

    connection.execute(
        """
        DELETE FROM auth_rate_limit_buckets
        WHERE bucket_key = %s
          AND window_started_at = %s;
        """,
        (
            bucket_key,
            window_start
        )
    )
