import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    """Create the phonebook table if it doesn't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id       SERIAL PRIMARY KEY,
        email    VARCHAR(100) NOT NULL UNIQUE,
        password VARCHAR(255) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS phonebook (
        id         SERIAL PRIMARY KEY,
        user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        name       VARCHAR(50) NOT NULL,
        phone      VARCHAR(20) NOT NULL,
        
        UNIQUE(user_id, phone)
    );
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized.")


if __name__ == "__main__":
    init_db()