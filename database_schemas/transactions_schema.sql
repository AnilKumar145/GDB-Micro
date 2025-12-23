-- ================================================================
-- TRANSACTIONS SERVICE DATABASE SCHEMA
-- Database: gdb_transactions_db
-- Purpose: Manage transactions, transfers, and transfer limits
-- ================================================================

-- ================================================================
-- TRANSACTIONS TABLE
-- Records all withdraw, deposit, and transfer operations
-- ================================================================
CREATE TABLE transactions (
    transaction_id BIGSERIAL PRIMARY KEY,
    from_account BIGINT,
    to_account BIGINT,
    amount NUMERIC(15, 2) NOT NULL CHECK (amount > 0),
    transaction_type VARCHAR(10) NOT NULL CHECK (transaction_type IN ('WITHDRAW', 'DEPOSIT', 'TRANSFER')),
    transfer_mode VARCHAR(10) CHECK (transfer_mode IN ('NEFT', 'RTGS', 'IMPS', 'UPI', 'CHEQUE')),
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING' CHECK (status IN ('PENDING', 'SUCCESS', 'FAILED', 'REVERSED')),
    idempotency_key VARCHAR(255) UNIQUE,
    transaction_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for common queries
CREATE INDEX idx_transactions_from_account ON transactions(from_account);
CREATE INDEX idx_transactions_to_account ON transactions(to_account);
CREATE INDEX idx_transactions_transaction_date ON transactions(transaction_date DESC);
CREATE INDEX idx_transactions_status ON transactions(status);
CREATE INDEX idx_transactions_idempotency_key ON transactions(idempotency_key);

-- ================================================================
-- DAILY TRANSFER LIMITS TABLE
-- Tracks aggregate transfers per account per day
-- ================================================================
CREATE TABLE daily_transfer_limits (
    limit_id BIGSERIAL PRIMARY KEY,
    account_number BIGINT NOT NULL,
    transfer_date DATE NOT NULL,
    total_amount NUMERIC(15, 2) NOT NULL DEFAULT 0.00,
    transaction_count INT NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(account_number, transfer_date)
);

-- Create index for daily limit lookup
CREATE INDEX idx_daily_limits_account_date ON daily_transfer_limits(account_number, transfer_date);

-- ================================================================
-- TRANSACTION LOGS TABLE
-- Audit trail for every transaction (DB + optional file logging)
-- ================================================================
CREATE TABLE transaction_logs (
    log_id BIGSERIAL PRIMARY KEY,
    transaction_id BIGINT NOT NULL REFERENCES transactions(transaction_id) ON DELETE CASCADE,
    from_account BIGINT,
    to_account BIGINT,
    amount NUMERIC(15, 2) NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    status VARCHAR(20) NOT NULL,
    log_message TEXT,
    log_file_path TEXT,
    log_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create index for transaction log lookup
CREATE INDEX idx_logs_transaction_id ON transaction_logs(transaction_id);
CREATE INDEX idx_logs_log_date ON transaction_logs(log_date DESC);
CREATE INDEX idx_logs_account ON transaction_logs(from_account, to_account);

-- ================================================================
-- TRANSACTION RULES TABLE
-- Stores privilege-based transfer limits
-- ================================================================
CREATE TABLE transfer_rules (
    rule_id BIGSERIAL PRIMARY KEY,
    privilege VARCHAR(10) NOT NULL UNIQUE CHECK (privilege IN ('PREMIUM', 'GOLD', 'SILVER')),
    daily_limit NUMERIC(15, 2) NOT NULL CHECK (daily_limit > 0),
    daily_transaction_count INT NOT NULL CHECK (daily_transaction_count > 0),
    description TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Insert default rules
INSERT INTO transfer_rules (privilege, daily_limit, daily_transaction_count, description) VALUES
    ('PREMIUM', 100000.00, 50, 'Premium privilege - highest limits'),
    ('GOLD', 50000.00, 30, 'Gold privilege - medium limits'),
    ('SILVER', 25000.00, 20, 'Silver privilege - basic limits');

-- ================================================================
-- FUNCTION TO UPDATE updated_at TIMESTAMP
-- ================================================================
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create triggers for updated_at
CREATE TRIGGER transactions_update_timestamp BEFORE UPDATE ON transactions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER daily_limits_update_timestamp BEFORE UPDATE ON daily_transfer_limits
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER transfer_rules_update_timestamp BEFORE UPDATE ON transfer_rules
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- VIEW FOR TRANSACTION SUMMARY
-- Shows transaction details with categorization
-- ================================================================
CREATE VIEW transaction_summary AS
SELECT 
    t.transaction_id,
    t.from_account,
    t.to_account,
    t.amount,
    t.transaction_type,
    t.transfer_mode,
    t.status,
    t.transaction_date,
    t.description,
    CASE 
        WHEN t.transaction_type = 'WITHDRAW' THEN 'Withdrawal'
        WHEN t.transaction_type = 'DEPOSIT' THEN 'Deposit'
        WHEN t.transaction_type = 'TRANSFER' THEN 'Fund Transfer'
        ELSE 'Unknown'
    END AS transaction_category,
    EXTRACT(DAY FROM t.transaction_date) AS day,
    EXTRACT(MONTH FROM t.transaction_date) AS month,
    EXTRACT(YEAR FROM t.transaction_date) AS year
FROM transactions t;

-- ================================================================
-- VIEW FOR DAILY ACCOUNT ACTIVITY
-- Summarizes all transactions per account per day
-- ================================================================
CREATE VIEW daily_account_activity AS
SELECT 
    COALESCE(t.from_account, t.to_account) AS account_number,
    DATE(t.transaction_date) AS activity_date,
    COUNT(*) AS transaction_count,
    SUM(t.amount) AS total_amount,
    SUM(CASE WHEN t.status = 'SUCCESS' THEN 1 ELSE 0 END) AS successful_count,
    SUM(CASE WHEN t.status = 'FAILED' THEN 1 ELSE 0 END) AS failed_count
FROM transactions t
WHERE t.status IN ('SUCCESS', 'FAILED')
GROUP BY account_number, activity_date;

-- ================================================================
-- END OF TRANSACTIONS SCHEMA
-- ================================================================
