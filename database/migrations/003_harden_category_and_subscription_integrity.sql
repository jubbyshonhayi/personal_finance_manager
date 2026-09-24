-- Hardens category and subscription integrity.
--
-- Categories must always have an explicit Income or Expense type.
-- Active subscriptions must use active plans, and plans with active
-- subscribers cannot be deactivated.

BEGIN;


-- Do not silently alter existing financial data. If any legacy
-- category has a NULL transaction type, the migration must stop
-- so the data can be reviewed before the constraint is applied.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM categories
        WHERE transaction_type IS NULL
    ) THEN
        RAISE EXCEPTION
            'Cannot make categories.transaction_type NOT NULL: NULL categories exist';
    END IF;
END;
$$;


ALTER TABLE categories
ALTER COLUMN transaction_type SET NOT NULL;


CREATE OR REPLACE FUNCTION check_active_subscription_plan()
RETURNS TRIGGER AS $$
DECLARE
    plan_active BOOLEAN;
BEGIN
    IF NEW.status = 'active' THEN
        SELECT is_active
        INTO plan_active
        FROM subscription_plans
        WHERE id = NEW.plan_id;

        IF plan_active IS DISTINCT FROM TRUE THEN
            RAISE EXCEPTION
                'Active subscription must use an active subscription plan';
        END IF;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER user_subscription_active_plan_check
BEFORE INSERT OR UPDATE OF plan_id, status
ON user_subscriptions
FOR EACH ROW
EXECUTE FUNCTION check_active_subscription_plan();


CREATE OR REPLACE FUNCTION prevent_active_plan_deactivation()
RETURNS TRIGGER AS $$
BEGIN
    IF OLD.is_active = TRUE
       AND NEW.is_active = FALSE
       AND EXISTS (
            SELECT 1
            FROM user_subscriptions
            WHERE plan_id = OLD.id
              AND status = 'active'
       ) THEN
        RAISE EXCEPTION
            'Subscription plan cannot be deactivated while active subscriptions exist';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER subscription_plan_deactivation_check
BEFORE UPDATE OF is_active
ON subscription_plans
FOR EACH ROW
EXECUTE FUNCTION prevent_active_plan_deactivation();


COMMIT;
