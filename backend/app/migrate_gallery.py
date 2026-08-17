from sqlalchemy import text
from app.database import engine

with engine.begin() as conn:
    for col in ("gallery", "tracks", "clips", "news"):
        conn.execute(
            text(
                f"ALTER TABLE artists "
                f"ADD COLUMN IF NOT EXISTS {col} JSONB"
            )
        )

print("Colonnes gallery/tracks/clips/news OK")