from sqlalchemy import text
from app.database import engine

with engine.begin() as conn:
    conn.execute(text(
        "ALTER TABLE artists "
        "ADD COLUMN IF NOT EXISTS manager_id VARCHAR(36)"
    ))

    conn.execute(text(
        "ALTER TABLE artists "
        "ADD COLUMN IF NOT EXISTS is_published BOOLEAN NOT NULL DEFAULT TRUE"
    ))

    conn.execute(text(
        "ALTER TABLE conversations "
        "ADD COLUMN IF NOT EXISTS trashed_at TIMESTAMPTZ NULL"
    ))

    conn.execute(text(
        "CREATE INDEX IF NOT EXISTS "
        "ix_conversations_trashed_at "
        "ON conversations (trashed_at)"
    ))

    conn.execute(text(
        "ALTER TABLE users "
        "ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500)"
    ))

print("Colonnes OK")