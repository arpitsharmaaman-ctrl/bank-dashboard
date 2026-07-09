-- ============================================================
-- Bank Domain Dashboard — SQL Queries
-- Run against data/bank.db (SQLite)
-- ============================================================

-- 1. Total balance by account type
SELECT account_type,
       COUNT(*) AS num_accounts,
       ROUND(SUM(balance), 2) AS total_balance,
       ROUND(AVG(balance), 2) AS avg_balance
FROM accounts
WHERE status = 'Active'
GROUP BY account_type
ORDER BY total_balance DESC;

-- 2. Customer balance summary by region
SELECT c.region,
       COUNT(DISTINCT c.customer_id) AS num_customers,
       ROUND(SUM(a.balance), 2) AS total_balance
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.region
ORDER BY total_balance DESC;

-- 3. Loan portfolio breakdown by type and status
SELECT loan_type,
       status,
       COUNT(*) AS num_loans,
       ROUND(SUM(principal_amount), 2) AS total_principal,
       ROUND(AVG(interest_rate), 2) AS avg_interest_rate
FROM loans
GROUP BY loan_type, status
ORDER BY loan_type, status;

-- 4. Default rate by loan type
SELECT loan_type,
       COUNT(*) AS total_loans,
       SUM(CASE WHEN status = 'Defaulted' THEN 1 ELSE 0 END) AS defaults,
       ROUND(100.0 * SUM(CASE WHEN status = 'Defaulted' THEN 1 ELSE 0 END) / COUNT(*), 2) AS default_rate_pct
FROM loans
GROUP BY loan_type
ORDER BY default_rate_pct DESC;

-- 5. Monthly transaction volume and value
SELECT strftime('%Y-%m', transaction_date) AS month,
       COUNT(*) AS num_transactions,
       ROUND(SUM(amount), 2) AS total_value
FROM transactions
GROUP BY month
ORDER BY month;

-- 6. Transaction breakdown by type
SELECT transaction_type,
       COUNT(*) AS num_transactions,
       ROUND(SUM(amount), 2) AS total_value,
       ROUND(AVG(amount), 2) AS avg_value
FROM transactions
GROUP BY transaction_type
ORDER BY total_value DESC;

-- 7. Fraud indicator summary
SELECT COUNT(*) AS total_transactions,
       SUM(is_fraud) AS flagged_fraud,
       ROUND(100.0 * SUM(is_fraud) / COUNT(*), 3) AS fraud_rate_pct
FROM transactions;

-- 8. Top 10 highest-value flagged fraud transactions with account/customer info
SELECT t.transaction_id, t.transaction_date, t.transaction_type, t.amount,
       a.account_id, a.account_type, c.name AS customer_name, c.region
FROM transactions t
JOIN accounts a ON t.account_id = a.account_id
JOIN customers c ON a.customer_id = c.customer_id
WHERE t.is_fraud = 1
ORDER BY t.amount DESC
LIMIT 10;

-- 9. Customers with highest total balance across all accounts
SELECT c.customer_id, c.name, c.region, c.credit_score,
       ROUND(SUM(a.balance), 2) AS total_balance
FROM customers c
JOIN accounts a ON c.customer_id = a.customer_id
GROUP BY c.customer_id
ORDER BY total_balance DESC
LIMIT 10;

-- 10. Dormant accounts that may need re-engagement
SELECT a.account_id, c.name, c.region, a.account_type, a.balance, a.opened_date
FROM accounts a
JOIN customers c ON a.customer_id = c.customer_id
WHERE a.status = 'Dormant'
ORDER BY a.balance DESC;
