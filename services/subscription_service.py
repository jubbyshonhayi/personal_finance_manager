from uuid import UUID

from models.subscriptions import UserSubscription


def create_free_subscription(
    connection,
    user_id: UUID
) -> UserSubscription:
    """
    Creates a permanent Free subscription for a user
    using the provided database connection.
    """
    row = connection.execute(
        """
        INSERT INTO user_subscriptions (
            user_id,
            plan_id,
            start_date,
            end_date,
            status
        )
        SELECT
            %s,
            id,
            CURRENT_TIMESTAMP,
            NULL,
            'active'
        FROM subscription_plans
        WHERE LOWER(plan_name) = LOWER('Free')
          AND is_active = TRUE

        RETURNING
            id,
            user_id,
            plan_id,
            start_date,
            end_date,
            status;
        """,
        (user_id,)
    ).fetchone()

    if row is None:
        raise RuntimeError(
            "Active Free subscription plan was not found."
        )

    return UserSubscription(
        id=row[0],
        user_id=row[1],
        plan_id=row[2],
        start_date=row[3],
        end_date=row[4],
        status=row[5]
    )