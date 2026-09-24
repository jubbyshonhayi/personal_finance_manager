-- Finalizes the category and subscription integrity hardening.
--
-- Migration 003 made category.transaction_type mandatory and added
-- active-subscription plan guards. This migration removes the now
-- obsolete NULL-oriented category logic and adds the subscription
-- pricing invariant.
--
-- Run this migration after 003.


BEGIN;


-- transaction_type is now NOT NULL, so NULLS NOT DISTINCT is no
-- longer required for category uniqueness.
DROP INDEX categories_user_type_name_unique;

CREATE UNIQUE INDEX categories_user_type_name_unique
ON categories (
    user_id,
    transaction_type,
    LOWER(category_name)
);


-- Keep the database trigger aligned with the non-null category
-- transaction_type invariant.
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


-- A free plan is non-recurring. Paid plans must define a
-- recurring billing interval.
ALTER TABLE subscription_plans
ADD CONSTRAINT subscription_plans_billing_rule
CHECK (
    (price = 0 AND billing_interval IS NULL)
    OR
    (price > 0 AND billing_interval IS NOT NULL)
);


COMMIT;
