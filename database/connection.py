from psycopg_pool import ConnectionPool

from config import DATABASE_URL


if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")


pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
    check=ConnectionPool.check_connection,
    max_lifetime=1800,
    max_idle=300,
    timeout=30,
    reconnect_timeout=60,
)