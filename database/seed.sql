-- Creates the default Free subscription plan required
-- for new user registration.
INSERT INTO subscription_plans (
    plan_name,
    description,
    price,
    currency,
    billing_interval,
    is_active
)
VALUES (
    'Free',
    'Basic access to the Personal Finance Manager.',
    0,
    'USD',
    NULL,
    TRUE
)
ON CONFLICT (LOWER(plan_name)) DO NOTHING;



-- Creates the default system transaction categories.
INSERT INTO categories (
    user_id,
    category_name,
    transaction_type
)
VALUES
    (NULL, 'Salary', 'Income'),
    (NULL, 'Business', 'Income'),
    (NULL, 'Investment', 'Income'),
    (NULL, 'Gift', 'Income'),
    (NULL, 'Other Income', 'Income'),

    (NULL, 'Food', 'Expense'),
    (NULL, 'Transport', 'Expense'),
    (NULL, 'Rent', 'Expense'),
    (NULL, 'Utilities', 'Expense'),
    (NULL, 'Education', 'Expense'),
    (NULL, 'Healthcare', 'Expense'),
    (NULL, 'Entertainment', 'Expense'),
    (NULL, 'Shopping', 'Expense'),
    (NULL, 'Other Expense', 'Expense')

ON CONFLICT (
    user_id,
    transaction_type,
    LOWER(category_name)
) DO NOTHING;