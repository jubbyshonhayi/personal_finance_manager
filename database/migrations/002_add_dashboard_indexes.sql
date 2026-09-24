-- Adds indexes for the dashboard's most common transaction queries.
--
-- These indexes improve filtering by user, currency, and date,
-- and improve retrieval of a user's most recent transactions.

BEGIN;


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


COMMIT;
