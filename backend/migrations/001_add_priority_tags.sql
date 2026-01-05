-- Migration: Add priority and tags columns to tasks table
-- Backward compatible: existing tasks get default values
-- Feature: 004-task-organization-features

-- Add priority column with default 'medium'
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS priority VARCHAR(10) DEFAULT 'medium' NOT NULL;

-- Add constraint for valid priority values (drop first if exists)
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'chk_tasks_priority'
    ) THEN
        ALTER TABLE tasks
        ADD CONSTRAINT chk_tasks_priority
        CHECK (priority IN ('high', 'medium', 'low'));
    END IF;
END $$;

-- Add tags column (PostgreSQL array) with default empty array
ALTER TABLE tasks
ADD COLUMN IF NOT EXISTS tags VARCHAR[] DEFAULT '{}' NOT NULL;

-- Create index for priority filtering
CREATE INDEX IF NOT EXISTS idx_tasks_priority ON tasks (priority);

-- Create GIN index for tag array queries (ANY/contains)
CREATE INDEX IF NOT EXISTS idx_tasks_tags ON tasks USING GIN (tags);
