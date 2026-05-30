"""
run_migration.py — Run inside the backend container to fix the database schema.

Usage (from project root):
    docker-compose exec backend python run_migration.py
"""
import os
import sys

# Load DATABASE_URL from environment (already set in the container)
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://meetmind_user:meetmind_password@db:5432/meetmind_db",
)

print(f"Connecting to: {DATABASE_URL.split('@')[-1]}")  # hide credentials

try:
    import psycopg2
except ImportError:
    print("ERROR: psycopg2 not found. Run this inside the backend container.")
    sys.exit(1)

MIGRATION_SQL = """
-- 1. Add owner_id to meetings if missing
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'meetings' AND column_name = 'owner_id'
    ) THEN
        ALTER TABLE meetings ADD COLUMN owner_id INTEGER;
        ALTER TABLE meetings ADD CONSTRAINT fk_meetings_owner
            FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE;
        CREATE INDEX IF NOT EXISTS ix_meetings_owner_id ON meetings(owner_id);
        RAISE NOTICE 'Added owner_id to meetings.';
    END IF;
END $$;

-- 2. action_items
CREATE TABLE IF NOT EXISTS action_items (
    id          SERIAL PRIMARY KEY,
    meeting_id  INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    task        VARCHAR(500) NOT NULL,
    owner       VARCHAR(255),
    due_date    TIMESTAMP,
    status      VARCHAR(50) NOT NULL DEFAULT 'pending',
    created_at  TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_action_items_id ON action_items(id);

-- 3. decisions
CREATE TABLE IF NOT EXISTS decisions (
    id             SERIAL PRIMARY KEY,
    meeting_id     INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    decision_text  VARCHAR(1000) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_decisions_id ON decisions(id);

-- 4. risks
CREATE TABLE IF NOT EXISTS risks (
    id          SERIAL PRIMARY KEY,
    meeting_id  INTEGER NOT NULL REFERENCES meetings(id) ON DELETE CASCADE,
    risk_text   VARCHAR(1000) NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_risks_id ON risks(id);

-- 5. trial_uses
CREATE TABLE IF NOT EXISTS trial_uses (
    id          SERIAL PRIMARY KEY,
    ip_address  VARCHAR(64) UNIQUE NOT NULL,
    used_at     TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS ix_trial_uses_id ON trial_uses(id);
CREATE INDEX IF NOT EXISTS ix_trial_uses_ip_address ON trial_uses(ip_address);
"""

try:
    conn = psycopg2.connect(DATABASE_URL)
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(MIGRATION_SQL)
    cur.close()
    conn.close()
    print("✅ Migration complete — all schema changes applied successfully.")
except Exception as e:
    print(f"❌ Migration failed: {e}")
    sys.exit(1)