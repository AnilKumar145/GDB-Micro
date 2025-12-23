-- ================================================================
-- AUTH SERVICE DATABASE SCHEMA
-- Database: gdb_auth_db
-- Purpose: Manage authentication, JWT tokens, and sessions
-- ================================================================

-- ================================================================
-- AUTH TOKENS TABLE
-- Stores issued JWT tokens for session management
-- ================================================================
CREATE TABLE auth_tokens (
    token_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    token_type VARCHAR(20) NOT NULL DEFAULT 'Bearer' CHECK (token_type IN ('Bearer', 'Basic')),
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    revoked_at TIMESTAMP,
    revocation_reason TEXT
);

-- Create indexes for common queries
CREATE INDEX idx_tokens_user_id ON auth_tokens(user_id);
CREATE INDEX idx_tokens_token ON auth_tokens(token);
CREATE INDEX idx_tokens_is_valid ON auth_tokens(is_valid);
CREATE INDEX idx_tokens_expires_at ON auth_tokens(expires_at);
CREATE INDEX idx_tokens_created_at ON auth_tokens(created_at DESC);

-- ================================================================
-- REFRESH TOKENS TABLE
-- Stores refresh tokens for obtaining new access tokens
-- ================================================================
CREATE TABLE refresh_tokens (
    refresh_token_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    token TEXT NOT NULL UNIQUE,
    is_valid BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    revoked_at TIMESTAMP
);

-- Create indexes for refresh token queries
CREATE INDEX idx_refresh_user_id ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_token ON refresh_tokens(token);
CREATE INDEX idx_refresh_is_valid ON refresh_tokens(is_valid);
CREATE INDEX idx_refresh_expires_at ON refresh_tokens(expires_at);

-- ================================================================
-- LOGIN ATTEMPTS TABLE
-- Track login attempts for security and audit purposes
-- ================================================================
CREATE TABLE login_attempts (
    attempt_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT,
    username VARCHAR(255),
    login_id VARCHAR(255),
    is_successful BOOLEAN NOT NULL DEFAULT FALSE,
    ip_address VARCHAR(45),
    user_agent TEXT,
    failure_reason VARCHAR(100),
    attempted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for login audit
CREATE INDEX idx_login_attempts_user_id ON login_attempts(user_id);
CREATE INDEX idx_login_attempts_login_id ON login_attempts(login_id);
CREATE INDEX idx_login_attempts_attempted_at ON login_attempts(attempted_at DESC);
CREATE INDEX idx_login_attempts_ip ON login_attempts(ip_address);

-- ================================================================
-- AUTHENTICATION SESSIONS TABLE
-- Stores active session information
-- ================================================================
CREATE TABLE auth_sessions (
    session_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    access_token_id BIGINT REFERENCES auth_tokens(token_id) ON DELETE CASCADE,
    refresh_token_id BIGINT REFERENCES refresh_tokens(refresh_token_id) ON DELETE CASCADE,
    device_info VARCHAR(500),
    ip_address VARCHAR(45),
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_activity_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL
);

-- Create indexes for session queries
CREATE INDEX idx_sessions_user_id ON auth_sessions(user_id);
CREATE INDEX idx_sessions_is_active ON auth_sessions(is_active);
CREATE INDEX idx_sessions_expires_at ON auth_sessions(expires_at);
CREATE INDEX idx_sessions_last_activity ON auth_sessions(last_activity_at DESC);

-- ================================================================
-- TOKEN BLACKLIST TABLE
-- Stores revoked tokens to prevent reuse
-- ================================================================
CREATE TABLE token_blacklist (
    blacklist_id BIGSERIAL PRIMARY KEY,
    token TEXT NOT NULL UNIQUE,
    token_type VARCHAR(20) NOT NULL CHECK (token_type IN ('ACCESS', 'REFRESH')),
    user_id BIGINT,
    blacklisted_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    reason VARCHAR(255)
);

-- Create index for blacklist lookup
CREATE INDEX idx_blacklist_token ON token_blacklist(token);
CREATE INDEX idx_blacklist_expires_at ON token_blacklist(expires_at);

-- ================================================================
-- PASSWORD RESET TABLE
-- Manages password reset tokens and requests
-- ================================================================
CREATE TABLE password_resets (
    reset_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    reset_token TEXT NOT NULL UNIQUE,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    used_at TIMESTAMP,
    ip_address VARCHAR(45)
);

-- Create index for reset token lookup
CREATE INDEX idx_password_reset_user_id ON password_resets(user_id);
CREATE INDEX idx_password_reset_token ON password_resets(reset_token);
CREATE INDEX idx_password_reset_is_used ON password_resets(is_used);

-- ================================================================
-- OAUTH TOKENS TABLE (Optional - for future OAuth2 integration)
-- ================================================================
CREATE TABLE oauth_tokens (
    oauth_token_id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    provider VARCHAR(50) NOT NULL CHECK (provider IN ('GOOGLE', 'GITHUB', 'MICROSOFT', 'FACEBOOK')),
    access_token TEXT NOT NULL,
    refresh_token TEXT,
    token_type VARCHAR(20) DEFAULT 'Bearer',
    expires_at TIMESTAMP,
    provider_user_id VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, provider)
);

-- Create index for OAuth token lookup
CREATE INDEX idx_oauth_user_id ON oauth_tokens(user_id);
CREATE INDEX idx_oauth_provider ON oauth_tokens(provider);

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

-- Create trigger for updated_at
CREATE TRIGGER oauth_update_timestamp BEFORE UPDATE ON oauth_tokens
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ================================================================
-- FUNCTION TO CLEANUP EXPIRED TOKENS (SCHEDULED)
-- ================================================================
CREATE OR REPLACE FUNCTION cleanup_expired_tokens()
RETURNS void AS $$
BEGIN
    -- Delete expired auth tokens
    DELETE FROM auth_tokens WHERE expires_at < CURRENT_TIMESTAMP AND is_valid = TRUE;
    
    -- Delete expired refresh tokens
    DELETE FROM refresh_tokens WHERE expires_at < CURRENT_TIMESTAMP AND is_valid = TRUE;
    
    -- Delete expired blacklisted tokens
    DELETE FROM token_blacklist WHERE expires_at < CURRENT_TIMESTAMP;
    
    -- Delete expired password reset tokens
    DELETE FROM password_resets WHERE expires_at < CURRENT_TIMESTAMP AND is_used = FALSE;
    
    -- Deactivate expired sessions
    UPDATE auth_sessions SET is_active = FALSE WHERE expires_at < CURRENT_TIMESTAMP AND is_active = TRUE;
END;
$$ LANGUAGE plpgsql;

-- ================================================================
-- VIEW FOR ACTIVE SESSIONS
-- Shows currently active user sessions
-- ================================================================
CREATE VIEW active_sessions_view AS
SELECT 
    s.session_id,
    s.user_id,
    s.device_info,
    s.ip_address,
    s.created_at,
    s.last_activity_at,
    s.expires_at,
    CASE 
        WHEN s.expires_at > CURRENT_TIMESTAMP THEN 'ACTIVE'
        ELSE 'EXPIRED'
    END AS session_status,
    (s.expires_at - CURRENT_TIMESTAMP) AS time_remaining
FROM auth_sessions s
WHERE s.is_active = TRUE;

-- ================================================================
-- VIEW FOR TOKEN STATISTICS
-- Shows token issuance statistics
-- ================================================================
CREATE VIEW token_statistics_view AS
SELECT 
    DATE(created_at) AS issue_date,
    COUNT(*) AS total_tokens_issued,
    SUM(CASE WHEN is_valid = TRUE THEN 1 ELSE 0 END) AS valid_tokens,
    SUM(CASE WHEN is_valid = FALSE THEN 1 ELSE 0 END) AS revoked_tokens
FROM auth_tokens
GROUP BY DATE(created_at);

-- ================================================================
-- END OF AUTH SCHEMA
-- ================================================================
