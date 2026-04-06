import sqlite3
from pathlib import Path

# Get project root relative to this file
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DB_PATH = PROJECT_ROOT / "cache.db"


def get_conn():
    return sqlite3.connect(DB_PATH)


def init_db():
    with get_conn() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS price_history (
            symbol TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (symbol, date)
        )
        """)


# -------------------------
# READ
# -------------------------

def get_cached_history(symbol: str) -> list[dict]:
    with get_conn() as conn:
        cursor = conn.execute("""
            SELECT date, open, high, low, close, volume
            FROM price_history
            WHERE symbol = ?
            ORDER BY date ASC
        """, (symbol,))

        rows = cursor.fetchall()

        return [
            {
                "Date": row[0],
                "Open": row[1],
                "High": row[2],
                "Low": row[3],
                "Close": row[4],
                "Volume": row[5],
            }
            for row in rows
        ]


# -------------------------
# WRITE
# -------------------------

def save_history(symbol: str, records: list[dict]):
    with get_conn() as conn:
        for row in records:
            conn.execute("""
                INSERT OR REPLACE INTO price_history
                (symbol, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                symbol,
                row["Date"],
                row.get("Open"),
                row.get("High"),
                row.get("Low"),
                row.get("Close"),
                row.get("Volume"),
            ))
