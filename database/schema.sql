-- Stores authentication and account information for registered users.
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username  VARCHAR(30) NOT NULL
        CHECK (btrim(username) <> ''),

    email VARCHAR(254) NOT NULL
        CHECK (btrim(email) <> ''),

    -- Stores a password hash, never the user's raw password.
    password_hash TEXT NOT NULL,

    date_joined TIMESTAMP WITH TIME ZONE NOT NULL
        DEFAULT CURRENT_TIMESTAMP
);


-- Prevents duplicate usernames regardless of letter case.
CREATE UNIQUE INDEX users_username_unique
ON users (LOWER(username));

-- Prevents duplicate email addresses regardless of letter case.
CREATE UNIQUE INDEX users_email_unique
ON users (LOWER(email));


-- Stores system and user-defined transaction categories.
--
-- user_id IS NULL  -> system category
-- user_id IS NOT NULL -> category owned by that user
CREATE TABLE categories (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID
        REFERENCES users(id)
        ON DELETE CASCADE,

    category_name VARCHAR(100) NOT NULL
        CHECK (btrim(category_name) <> ''),

    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN ('Income', 'Expense'))
);


-- Speeds up retrieval and foreign-key deletion checks for
-- user-owned categories.
CREATE INDEX categories_user_id_idx
ON categories (user_id);


-- Prevents duplicate category names for the same owner
-- and transaction type.
CREATE UNIQUE INDEX categories_user_type_name_unique
ON categories (
    user_id,
    transaction_type,
    LOWER(category_name)
);


-- Stores individual financial transactions made by users.
CREATE TABLE transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    amount DECIMAL(19, 4) NOT NULL
        CHECK (amount > 0),

    currency TEXT NOT NULL
        CHECK (currency ~ '^[A-Z]{3}$'),

    transaction_type TEXT NOT NULL
        CHECK (transaction_type IN ('Income', 'Expense')),

    category_id UUID NOT NULL
        REFERENCES categories(id),

    description VARCHAR(500),

    transaction_date DATE NOT NULL
);


-- Speeds up queries that retrieve transactions for a user
-- and helps PostgreSQL process the user foreign-key cascade.
CREATE INDEX transactions_user_id_idx
ON transactions (user_id);


-- Speeds up joins and foreign-key checks involving categories.
CREATE INDEX transactions_category_id_idx
ON transactions (category_id);


-- Ensures a transaction can only use:
--   1. a system category, or
--   2. a private category owned by the same user.
--
-- Ensures that the transaction type matches the category type.
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

    IF category_owner IS NULL THEN
        -- System category: ownership check is not required.
        NULL;
    ELSIF category_owner <> NEW.user_id THEN
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


CREATE TRIGGER transaction_category_check
BEFORE INSERT OR UPDATE OF user_id, category_id, transaction_type
ON transactions
FOR EACH ROW
EXECUTE FUNCTION check_transaction_category();


-- Prevents a category's ownership or transaction type from
-- changing after creation.
--
-- If a different category type is needed later, the application
-- should create a new category instead of changing an existing
-- category that may already be referenced by transactions.
CREATE OR REPLACE FUNCTION prevent_category_definition_change()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.user_id IS DISTINCT FROM OLD.user_id THEN
        RAISE EXCEPTION
            'Category ownership cannot be changed';
    END IF;

    IF NEW.transaction_type IS DISTINCT FROM OLD.transaction_type THEN
        RAISE EXCEPTION
            'Category transaction type cannot be changed';
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER category_definition_immutable
BEFORE UPDATE OF user_id, transaction_type
ON categories
FOR EACH ROW
EXECUTE FUNCTION prevent_category_definition_change();


-- Stores monthly category budgets.
--
-- Each budget is a recurring monthly spending limit for one
-- expense category and one currency.
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


-- Speeds up financial report queries that filter transactions
-- by user, currency, and transaction date.
CREATE INDEX transactions_user_currency_date_idx
ON transactions (
    user_id,
    currency,
    transaction_date
);


-- Speeds up recent-transaction queries by matching the
-- user's filtering and descending date ordering.
CREATE INDEX transactions_user_date_desc_idx
ON transactions (
    user_id,
    transaction_date DESC,
    id DESC
);


-- Stores the subscription plans offered by the application.
--
-- billing_interval is NULL for plans without recurring billing,
-- such as the permanent Free plan.
CREATE TABLE subscription_plans (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    plan_name TEXT NOT NULL
        CHECK (btrim(plan_name) <> ''),

    description TEXT,

    price DECIMAL(19, 4) NOT NULL
        CHECK (price >= 0),

    currency TEXT NOT NULL
        CHECK (currency ~ '^[A-Z]{3}$'),

    billing_interval TEXT
        CHECK (billing_interval IN ('monthly', 'yearly')),

    CHECK (
        (price = 0 AND billing_interval IS NULL)
        OR
        (price > 0 AND billing_interval IS NOT NULL)
    ),

    is_active BOOLEAN NOT NULL DEFAULT TRUE
);


-- Prevents duplicate plan names regardless of letter case.
CREATE UNIQUE INDEX subscription_plans_name_unique
ON subscription_plans (LOWER(plan_name));


-- Stores a user's subscription history.
--
-- A subscription belongs to a user and therefore disappears
-- when that user account is deleted.
CREATE TABLE user_subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES users(id)
        ON DELETE CASCADE,

    plan_id UUID NOT NULL
        REFERENCES subscription_plans(id),

    start_date TIMESTAMP WITH TIME ZONE NOT NULL,

    end_date TIMESTAMP WITH TIME ZONE,

    status TEXT NOT NULL
        CHECK (
            status IN (
                'active',
                'cancelled',
                'expired',
                'suspended'
            )
        ),

    CHECK (
        end_date IS NULL
        OR end_date >= start_date
    )
);


-- Speeds up queries for a user's subscription history
-- and helps PostgreSQL process the user foreign-key cascade.
CREATE INDEX user_subscriptions_user_id_idx
ON user_subscriptions (user_id);


-- Speeds up queries for subscriptions associated with a plan
-- and helps enforce the plan foreign key efficiently.
CREATE INDEX user_subscriptions_plan_id_idx
ON user_subscriptions (plan_id);


-- Ensures a user can have at most one active subscription.
CREATE UNIQUE INDEX user_subscriptions_one_active_idx
ON user_subscriptions (user_id)
WHERE status = 'active';


CREATE OR REPLACE FUNCTION check_active_subscription_plan()
RETURNS TRIGGER AS $
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
$ LANGUAGE plpgsql;


CREATE TRIGGER user_subscription_active_plan_check
BEFORE INSERT OR UPDATE OF plan_id, status
ON user_subscriptions
FOR EACH ROW
EXECUTE FUNCTION check_active_subscription_plan();


CREATE OR REPLACE FUNCTION prevent_active_plan_deactivation()
RETURNS TRIGGER AS $
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
$ LANGUAGE plpgsql;


CREATE TRIGGER subscription_plan_deactivation_check
BEFORE UPDATE OF is_active
ON subscription_plans
FOR EACH ROW
EXECUTE FUNCTION prevent_active_plan_deactivation();



-- Stores one-time password-reset tokens for users.
CREATE TABLE password_reset_tokens (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,

    -- Only the hashed token is stored; the raw token is sent to the user.
    token_hash TEXT NOT NULL UNIQUE,

    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,

    -- NULL means the token has not been used.
    used_at TIMESTAMP WITH TIME ZONE,

    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX password_reset_tokens_user_id_idx
ON password_reset_tokens (user_id);

CREATE INDEX password_reset_tokens_expires_at_idx
ON password_reset_tokens (expires_at);

-- Stores fixed-window counters used to limit authentication requests.
CREATE TABLE auth_rate_limit_buckets (
    bucket_key TEXT NOT NULL,
    window_started_at TIMESTAMP WITH TIME ZONE NOT NULL,
    request_count INTEGER NOT NULL DEFAULT 0 CHECK (request_count >= 0),
    PRIMARY KEY (bucket_key, window_started_at)
);

CREATE INDEX auth_rate_limit_buckets_window_idx
ON auth_rate_limit_buckets (window_started_at);