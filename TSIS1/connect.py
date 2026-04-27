import os
import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Apply schema.sql and procedures.sql to the database."""
    base = os.path.dirname(os.path.abspath(__file__))
    conn = get_connection()
    cur = conn.cursor()
    try:
        for filename in ("schema.sql", "procedures.sql"):
            path = os.path.join(base, filename)
            with open(path, encoding="utf-8") as f:
                cur.execute(f.read())
        conn.commit()
        print("✅ Database initialised.")
    except Exception as e:
        conn.rollback()
        print(f"❌ Init error: {e}")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    init_db()
