

import os
from sqlalchemy import create_engine, text

# ── DATABASE URL ─────────────────────────────────────
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:password@db:5432/rh_db_connect"
)

# ── ENGINE ───────────────────────────────────────────
engine = create_engine(DATABASE_URL)

# ── TEST CONNECTION ──────────────────────────────────
def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        print("✅ Connexion PostgreSQL réussie")

    except Exception as e:
        print(f"❌ Connexion échouée : {e}")

# ── GET TABLES ───────────────────────────────────────
def get_tables():

    with engine.connect() as conn:

        result = conn.execute(text("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """))

        tables = [row[0] for row in result]

        print("📋 Tables disponibles :", tables)

        return tables

# ── MAIN ─────────────────────────────────────────────
if __name__ == "__main__":
    test_connection()
    get_tables()