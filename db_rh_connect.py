import os
from sqlalchemy import create_engine, text

# ── Configuration ────────────────────────────────────────────────
DB_USER     = os.environ.get("USER", "valerianbarreau")
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "rh_database"

# ── Connexion ────────────────────────────────────────────────────
engine = create_engine(
    f"postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ── Test de connexion ────────────────────────────────────────────
def test_connection():
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print(f"✅ Connecté à '{DB_NAME}' en tant que '{DB_USER}'")
    except Exception as e:
        print(f"❌ Connexion échouée : {e}")

def get_tables():
    """Affiche toutes les tables disponibles dans la base."""
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


if __name__ == "__main__":
    test_connection()
    get_tables()

