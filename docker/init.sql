-- AI Web Automation Agent Database Schema
-- This script will automatically run when PostgreSQL container starts

-- Create automation tasks table
CREATE TABLE IF NOT EXISTS automation_tasks (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) UNIQUE NOT NULL,
    prompt TEXT NOT NULL,
    website_url VARCHAR(2048) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    
    -- Results
    generated_code TEXT NULL,
    execution_result JSONB NULL,
    error_message TEXT NULL,
    screenshots JSONB NULL,
    
    -- Metadata
    attempt_count INTEGER DEFAULT 0,
    max_attempts INTEGER DEFAULT 3,
    execution_time_ms INTEGER NULL,
    
    -- User tracking
    user_id VARCHAR(255) NULL,
    session_id VARCHAR(255) NULL
);

-- Create attempt details table for tracking each attempt
CREATE TABLE IF NOT EXISTS automation_attempts (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    attempt_number INTEGER NOT NULL,
    status VARCHAR(50) NOT NULL,
    generated_code TEXT NULL,
    execution_result JSONB NULL,
    error_message TEXT NULL,
    screenshots JSONB NULL,
    execution_time_ms INTEGER NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES automation_tasks(task_id) ON DELETE CASCADE,
    UNIQUE(task_id, attempt_number)
);

-- Create automation logs table
CREATE TABLE IF NOT EXISTS automation_logs (
    id SERIAL PRIMARY KEY,
    task_id VARCHAR(255) NOT NULL,
    level VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    source VARCHAR(100) NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (task_id) REFERENCES automation_tasks(task_id) ON DELETE CASCADE
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_automation_tasks_status ON automation_tasks(status);
CREATE INDEX IF NOT EXISTS idx_automation_tasks_created_at ON automation_tasks(created_at);
CREATE INDEX IF NOT EXISTS idx_automation_tasks_task_id ON automation_tasks(task_id);

CREATE INDEX IF NOT EXISTS idx_automation_attempts_task_id ON automation_attempts(task_id);
CREATE INDEX IF NOT EXISTS idx_automation_attempts_attempt_number ON automation_attempts(attempt_number);

CREATE INDEX IF NOT EXISTS idx_automation_logs_task_id ON automation_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_automation_logs_timestamp ON automation_logs(timestamp);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_automation_tasks_updated_at 
    BEFORE UPDATE ON automation_tasks 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();

-- Removed sample data to prevent duplicate key errors
-- Sample data can be added manually through the API or PgAdmin if needed

-- Create user for application (if not exists)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_user WHERE usename = 'app_user') THEN
        CREATE USER app_user WITH PASSWORD 'app_password_2024';
    END IF;
END
$$;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE ai_automation TO app_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO app_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO app_user; 