-- Reconciles category and subscription integrity after migrations 003 and 004.
--
-- This migration is intentionally corrective and idempotent where possible.
-- It brings an existing database to the same integrity state represented
-- by database/schema.sql without rewriting the historical migrations.


BEGIN;


-- Category transaction types must never be NULL.
DO $$
BEGIN
    IF EXISTS (
        SELECT 1
        FROM categories
        WHERE transaction_type IS NULL
    ) THEN
        RAISE EXCEPTION
            'Cannot finalize category integrity: NULL transaction types exist';
    END IF;
END;
$$;


ALTER TABLE categories
ALTER COLUMN transaction_type SET NOT NULL;


-- Replace the obsolete NULLS NOT DISTINCT index with the normal
-- uniqueness rule now that transaction_type is guaranteed non-null.
DROP INDEX IF EXISTS categories_user_type_name_unique;

CREATE UNIQUE INDEX categories_user_type_name_unique
ON categories (
    user_id,
    transaction_type,
    LOWER(category_name)
);


-- Keep transaction/category integrity aligned with the final
-- non-null transaction_type invariant.
CREATE OR REPLACE FUNCTION check_transaction_category()
RETURNS TRIGGER AS $$
DECLARE
    category_owner UUID;
    category_type TEXT;
BEGIN
    SELECT user_id, transaction_type
    INTO category_owner, category_type
    FROM categories
    WHERE id = NEW.category_id;

    IF category_owner IS NOT NULL
       AND category_owner <> NEW.user_id THEN
        RAISE EXCEPTION
            'Transaction cannot use another user''s category';
    END IF;

    IF category_type <> NEW.transaction_type THEN
        RAISE EXCEPTION
            'Transaction type does not match category type';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


-- The trigger may already exist from migration 003. Create it only
-- when it is missing so this corrective migration is safe to rerun.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'user_subscription_active_plan_check'
          AND tgrelid = 'user_subscriptions'::regclass
    ) THEN
        CREATE TRIGGER user_subscription_active_plan_check
        BEFORE INSERT OR UPDATE OF plan_id, status
        ON user_subscriptions
        FOR EACH ROW
        EXECUTE FUNCTION check_active_subscription_plan();
    END IF;
END;
$$;


-- Recreate the active-subscription guard function even when the
-- original migration has already created it.
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


-- Recreate the plan-deactivation guard function.
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


-- Create the deactivation trigger only when it is missing.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_trigger
        WHERE tgname = 'subscription_plan_deactivation_check'
          AND tgrelid = 'subscription_plans'::regclass
    ) THEN
        CREATE TRIGGER subscription_plan_deactivation_check
        BEFORE UPDATE OF is_active
        ON subscription_plans
        FOR EACH ROW
        EXECUTE FUNCTION prevent_active_plan_deactivation();
    END IF;
END;
$$;


-- Enforce the pricing/billing relationship when the constraint
-- is not already present.
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM pg_constraint
        WHERE conname = 'subscription_plans_billing_rule'
          AND conrelid = 'subscription_plans'::regclass
    ) THEN
        ALTER TABLE subscription_plans
        ADD CONSTRAINT subscription_plans_billing_rule
        CHECK (
            (price = 0 AND billing_interval IS NULL)
            OR
            (price > 0 AND billing_interval IS NOT NULL)
        );
    END IF;
END;
$$;


COMMIT;
