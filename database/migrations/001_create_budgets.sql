-- Creates monthly category budgets for users.
--
-- A budget is a recurring monthly spending limit for one
-- expense category and one currency.

BEGIN;


CREATE TABLE budgets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    category_id UUID NOT NULL
        REFERENCES categories(id),

    currency TEXT NOT NULL
        CHECK (currency ~ '^[A-Z]{3}$'),

    monthly_limit DECIMAL(19, 4) NOT NULL
        CHECK (monthly_limit > 0),

    created_at TIMESTAMP WITH TIME ZONE NOT NULL
        DEFAULT CURRENT_TIMESTAMP,

    updated_at TIMESTAMP WITH TIME ZONE NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- A user can have only one monthly budget for a given
-- expense category and currency.
CREATE UNIQUE INDEX budgets_user_category_currency_unique
ON budgets (
    user_id,
    category_id,
    currency
);


-- Speeds up category foreign-key checks and category-related
-- budget lookups.
CREATE INDEX budgets_category_id_idx
ON budgets (category_id);


-- Ensures a budget can only use:
--   1. a system expense category, or
--   2. a private expense category owned by the same user.
CREATE OR REPLACE FUNCTION check_budget_category()
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
            'Budget cannot use another user''s category';
    END IF;

    IF category_type IS DISTINCT FROM 'Expense' THEN
        RAISE EXCEPTION
            'Budget category must be an expense category';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER budget_category_check
BEFORE INSERT OR UPDATE OF user_id, category_id
ON budgets
FOR EACH ROW
EXECUTE FUNCTION check_budget_category();


-- Speeds up budget progress queries that filter transactions
-- by user, category, currency, and transaction date.
CREATE INDEX transactions_budget_progress_idx
ON transactions (
    user_id,
    category_id,
    currency,
    transaction_date
);


COMMIT;
