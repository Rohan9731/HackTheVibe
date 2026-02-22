"""
Database layer — SQLite with per-user data isolation.
Every table has user_id so each user gets their own experience.
"""
import sqlite3, os
from contextlib import contextmanager

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "vibeshield.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

@contextmanager
def get_db_context():
    conn = get_db()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def _row(r):
    return dict(r) if r else None

def init_db():
    with get_db_context() as c:
        # Check if old schema (no user_id) — if so, drop and recreate
        needs_migration = False
        try:
            c.execute("SELECT user_id FROM transactions LIMIT 0")
        except Exception:
            needs_migration = True
        if needs_migration:
            c.executescript("""
                DROP TABLE IF EXISTS transactions;
                DROP TABLE IF EXISTS moods;
                DROP TABLE IF EXISTS savings_goals;
                DROP TABLE IF EXISTS accountability_contacts;
            """)
        c.executescript("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                amount REAL NOT NULL,
                merchant TEXT NOT NULL,
                category TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                impulse_score REAL DEFAULT 0,
                risk_level TEXT DEFAULT 'low',
                was_paused INTEGER DEFAULT 0,
                was_overridden INTEGER DEFAULT 0,
                was_cancelled INTEGER DEFAULT 0,
                pause_duration REAL DEFAULT 0,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS moods (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                mood TEXT NOT NULL,
                emoji TEXT NOT NULL,
                intensity INTEGER DEFAULT 5,
                timestamp TEXT NOT NULL,
                notes TEXT DEFAULT ''
            );
            CREATE TABLE IF NOT EXISTS savings_goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                target_amount REAL NOT NULL,
                current_amount REAL DEFAULT 0,
                deadline TEXT,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS accountability_contacts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                name TEXT NOT NULL,
                phone TEXT DEFAULT '',
                email TEXT DEFAULT '',
                is_active INTEGER DEFAULT 1
            );
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL UNIQUE,
                lock_duration INTEGER DEFAULT 20,
                lock_sensitivity TEXT DEFAULT 'medium',
                enable_accountability INTEGER DEFAULT 1,
                enable_breathing INTEGER DEFAULT 1,
                enable_mood_alerts INTEGER DEFAULT 1
            );
            CREATE INDEX IF NOT EXISTS idx_tx_user ON transactions(user_id);
            CREATE INDEX IF NOT EXISTS idx_mood_user ON moods(user_id);
            CREATE INDEX IF NOT EXISTS idx_sg_user ON savings_goals(user_id);
            CREATE INDEX IF NOT EXISTS idx_us_user ON user_settings(user_id);
        """)


# ─────────────────── Transactions ───────────────────

def insert_transaction(user_id: str, data: dict) -> int:
    with get_db_context() as c:
        cur = c.execute(
            """INSERT INTO transactions
               (user_id, amount, merchant, category, timestamp,
                impulse_score, risk_level, was_paused, was_overridden, was_cancelled, notes)
               VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
            (user_id, data["amount"], data["merchant"], data["category"],
             data["timestamp"], data.get("impulse_score", 0),
             data.get("risk_level", "low"), int(data.get("was_paused", 0)),
             int(data.get("was_overridden", 0)), int(data.get("was_cancelled", 0)),
             data.get("notes", "")))
        return cur.lastrowid

def get_all_transactions(user_id: str, limit: int = 500) -> list[dict]:
    with get_db_context() as c:
        rows = c.execute(
            "SELECT * FROM transactions WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)).fetchall()
        return [_row(r) for r in rows]

def get_committed_transactions(user_id: str, limit: int = 500) -> list[dict]:
    """Only transactions that went through (not cancelled)."""
    with get_db_context() as c:
        rows = c.execute(
            "SELECT * FROM transactions WHERE user_id=? AND was_cancelled=0 ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)).fetchall()
        return [_row(r) for r in rows]

def get_transaction_count(user_id: str) -> int:
    with get_db_context() as c:
        r = c.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id=?", (user_id,)).fetchone()
        return r["cnt"] if r else 0

def update_transaction_outcome(tx_id: int, was_paused: bool, was_overridden: bool,
                                was_cancelled: bool, pause_duration: float = 0):
    with get_db_context() as c:
        c.execute(
            "UPDATE transactions SET was_paused=?, was_overridden=?, was_cancelled=?, pause_duration=? WHERE id=?",
            (int(was_paused), int(was_overridden), int(was_cancelled), pause_duration, tx_id))


# ─────────────────── Moods ───────────────────

def insert_mood(user_id: str, data: dict) -> int:
    with get_db_context() as c:
        cur = c.execute(
            "INSERT INTO moods (user_id, mood, emoji, intensity, timestamp, notes) VALUES (?,?,?,?,?,?)",
            (user_id, data["mood"], data["emoji"], data.get("intensity", 5),
             data["timestamp"], data.get("notes", "")))
        return cur.lastrowid

def get_all_moods(user_id: str, limit: int = 200) -> list[dict]:
    with get_db_context() as c:
        rows = c.execute(
            "SELECT * FROM moods WHERE user_id=? ORDER BY timestamp DESC LIMIT ?",
            (user_id, limit)).fetchall()
        return [_row(r) for r in rows]

def get_recent_mood(user_id: str):
    with get_db_context() as c:
        r = c.execute(
            "SELECT * FROM moods WHERE user_id=? ORDER BY timestamp DESC LIMIT 1",
            (user_id,)).fetchone()
        return _row(r)


# ─────────────────── Savings Goals ───────────────────

def get_savings_goals(user_id: str) -> list[dict]:
    with get_db_context() as c:
        rows = c.execute("SELECT * FROM savings_goals WHERE user_id=? ORDER BY id", (user_id,)).fetchall()
        return [_row(r) for r in rows]

def insert_savings_goal(user_id: str, data: dict) -> int:
    with get_db_context() as c:
        cur = c.execute(
            "INSERT INTO savings_goals (user_id, name, target_amount, current_amount, deadline, created_at) VALUES (?,?,?,?,?,?)",
            (user_id, data["name"], data["target_amount"],
             data.get("current_amount", 0), data.get("deadline", ""), data["created_at"]))
        return cur.lastrowid

def update_savings_goal_amount(goal_id: int, add_amount: float):
    with get_db_context() as c:
        c.execute("UPDATE savings_goals SET current_amount = current_amount + ? WHERE id=?",
                  (add_amount, goal_id))


# ─────────────────── Accountability Contacts ───────────────────

def get_accountability_contacts(user_id: str) -> list[dict]:
    with get_db_context() as c:
        rows = c.execute(
            "SELECT * FROM accountability_contacts WHERE user_id=? AND is_active=1",
            (user_id,)).fetchall()
        return [_row(r) for r in rows]

def insert_accountability_contact(user_id: str, data: dict) -> int:
    with get_db_context() as c:
        cur = c.execute(
            "INSERT INTO accountability_contacts (user_id, name, phone, email) VALUES (?,?,?,?)",
            (user_id, data["name"], data.get("phone", ""), data.get("email", "")))
        return cur.lastrowid


# ─────────────────── User Settings ───────────────────

def get_user_settings(user_id: str) -> dict:
    with get_db_context() as c:
        r = c.execute("SELECT * FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
        if r:
            return _row(r)
        # Return defaults
        return {
            "user_id": user_id,
            "lock_duration": 20,
            "lock_sensitivity": "medium",
            "enable_accountability": 1,
            "enable_breathing": 1,
            "enable_mood_alerts": 1,
        }

def update_user_settings(user_id: str, settings: dict):
    with get_db_context() as c:
        existing = c.execute("SELECT id FROM user_settings WHERE user_id=?", (user_id,)).fetchone()
        if existing:
            c.execute(
                """UPDATE user_settings SET lock_duration=?, lock_sensitivity=?,
                   enable_accountability=?, enable_breathing=?, enable_mood_alerts=?
                   WHERE user_id=?""",
                (settings.get("lock_duration", 20), settings.get("lock_sensitivity", "medium"),
                 int(settings.get("enable_accountability", 1)), int(settings.get("enable_breathing", 1)),
                 int(settings.get("enable_mood_alerts", 1)), user_id))
        else:
            c.execute(
                """INSERT INTO user_settings
                   (user_id, lock_duration, lock_sensitivity, enable_accountability, enable_breathing, enable_mood_alerts)
                   VALUES (?,?,?,?,?,?)""",
                (user_id, settings.get("lock_duration", 20), settings.get("lock_sensitivity", "medium"),
                 int(settings.get("enable_accountability", 1)), int(settings.get("enable_breathing", 1)),
                 int(settings.get("enable_mood_alerts", 1))))


# ─────────────────── User Data Mgmt ───────────────────

def clear_user_data(user_id: str):
    with get_db_context() as c:
        for tbl in ["transactions", "moods", "savings_goals", "accountability_contacts", "user_settings"]:
            c.execute(f"DELETE FROM {tbl} WHERE user_id=?", (user_id,))

def get_user_stats(user_id: str) -> dict:
    with get_db_context() as c:
        tx = c.execute("SELECT COUNT(*) as cnt FROM transactions WHERE user_id=?", (user_id,)).fetchone()
        saved = c.execute(
            "SELECT COUNT(*) as cnt, COALESCE(SUM(amount),0) as total FROM transactions WHERE user_id=? AND was_cancelled=1",
            (user_id,)).fetchone()
        moods_n = c.execute("SELECT COUNT(*) as cnt FROM moods WHERE user_id=?", (user_id,)).fetchone()
        return {
            "total_transactions": tx["cnt"],
            "cancelled_count": saved["cnt"],
            "money_saved": round(saved["total"], 0),
            "mood_entries": moods_n["cnt"],
        }
