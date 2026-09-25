-- Adds request-level idempotency to transaction creation.
-- Existing transactions receive unique request IDs before the
-- column becomes required.
BEGIN;

ALTER TABLE transactions
ADD COLUMN request_id UUID;

UPDATE transactions
SET request_id = gen_random_uuid()
WHERE request_id IS NULL;

ALTER TABLE transactions
ALTER COLUMN request_id SET NOT NULL;

CREATE UNIQUE INDEX transactions_user_request_id_unique
ON transactions (user_id, request_id);

INSERT INTO schema_migrations (version)
VALUES (1);

COMMIT;
