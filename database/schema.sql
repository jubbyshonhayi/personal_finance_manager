-- Stores authentication and account information for registered users.
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    username  VARCHAR(30) NOT NULL
        CHECK (btrim(username) <> ''),

    email VARCHAR(254) TEXT NOT NULL
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

    transaction_type TEXT
        CHECK (transaction_type IN ('Income', 'Expense'))
);


-- Speeds up retrieval and foreign-key deletion checks for
-- user-owned categories.
CREATE INDEX categories_user_id_idx
ON categories (user_id);


-- Prevents duplicate category names for the same owner
-- and transaction type.
--
-- NULL transaction types are treated as equal so a category
-- such as "Other" cannot be duplicated for the same owner.
CREATE UNIQUE INDEX categories_user_type_name_unique
ON categories (
    user_id,
    transaction_type,
    LOWER(category_name)
) NULLS NOT DISTINCT;


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
-- Also ensures that a category restricted to Income or Expense
-- can only be used by transactions of the matching type.
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

    IF category_type IS NOT NULL
       AND category_type <> NEW.transaction_type THEN
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