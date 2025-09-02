-- Initialize H4WK5INT database
-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_investigations_user_id ON investigations(user_id);
CREATE INDEX IF NOT EXISTS idx_investigations_status ON investigations(status);
CREATE INDEX IF NOT EXISTS idx_osint_results_investigation_id ON osint_results(investigation_id);
CREATE INDEX IF NOT EXISTS idx_osint_results_module_name ON osint_results(module_name);
CREATE INDEX IF NOT EXISTS idx_osint_results_status ON osint_results(status);
CREATE INDEX IF NOT EXISTS idx_reports_user_id ON reports(user_id);
CREATE INDEX IF NOT EXISTS idx_reports_investigation_id ON reports(investigation_id);
CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_jti ON blacklisted_tokens(jti);
CREATE INDEX IF NOT EXISTS idx_blacklisted_tokens_user_id ON blacklisted_tokens(user_id);

-- Insert sample data (optional)
-- This will be handled by the Flask application initialization