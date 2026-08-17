from sqlalchemy import text
from app.database import engine

with engine.begin() as c:
    c.execute(text(
        "ALTER TABLE users ADD COLUMN IF NOT EXISTS "
        "is_blocked BOOLEAN NOT NULL DEFAULT FALSE"
    ))

    c.execute(text(
        "ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'admin'"
    ))

print("SQL OK: is_blocked + admin")