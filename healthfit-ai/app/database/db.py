import json, os, sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone

DB_PATH = os.getenv("DATABASE_PATH", "healthfit.db")


@contextmanager
def _conn():
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    try:
        yield c
        c.commit()
    finally:
        c.close()


def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS profiles (
            user_id TEXT PRIMARY KEY, conditions TEXT NOT NULL, allergies TEXT NOT NULL,
            language TEXT NOT NULL, updated_at TEXT NOT NULL)""")


def save_profile(p: dict):
    with _conn() as c:
        c.execute("""INSERT INTO profiles(user_id,conditions,allergies,language,updated_at)
            VALUES(?,?,?,?,?) ON CONFLICT(user_id) DO UPDATE SET
            conditions=excluded.conditions, allergies=excluded.allergies,
            language=excluded.language, updated_at=excluded.updated_at""",
                  (p["user_id"], json.dumps(p["conditions"]), json.dumps(p["allergies"]),
                   p["language"], datetime.now(timezone.utc).isoformat()))


def get_profile(user_id: str):
    with _conn() as c:
        r = c.execute("SELECT * FROM profiles WHERE user_id=?", (user_id,)).fetchone()
    if not r:
        return None
    return {"user_id": r["user_id"], "conditions": json.loads(r["conditions"]),
            "allergies": json.loads(r["allergies"]), "language": r["language"]}


def delete_profile(user_id: str) -> bool:
    with _conn() as c:
        return c.execute("DELETE FROM profiles WHERE user_id=?", (user_id,)).rowcount > 0
