import psycopg2
from config import DB_CONFIG


def get_connection():
    return psycopg2.connect(**DB_CONFIG)


def init_db():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id       SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL
        );

        CREATE TABLE IF NOT EXISTS game_sessions (
            id            SERIAL PRIMARY KEY,
            player_id     INTEGER REFERENCES players(id),
            score         INTEGER   NOT NULL,
            level_reached INTEGER   NOT NULL,
            played_at     TIMESTAMP DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()


def get_or_create_player(username: str) -> int:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO players (username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
        (username,),
    )
    conn.commit()
    cur.execute("SELECT id FROM players WHERE username = %s", (username,))
    player_id = cur.fetchone()[0]
    cur.close()
    conn.close()
    return player_id


def save_session(player_id: int, score: int, level_reached: int) -> None:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO game_sessions (player_id, score, level_reached) VALUES (%s, %s, %s)",
        (player_id, score, level_reached),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_leaderboard() -> list:
    """Returns list of (username, score, level_reached, played_at) top 10."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT p.username, gs.score, gs.level_reached, gs.played_at
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC
        LIMIT 10
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


def get_personal_best(player_id: int) -> int:
    """Returns the player's highest score ever, or 0."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT MAX(score) FROM game_sessions WHERE player_id = %s",
        (player_id,),
    )
    result = cur.fetchone()[0]
    cur.close()
    conn.close()
    return result or 0
