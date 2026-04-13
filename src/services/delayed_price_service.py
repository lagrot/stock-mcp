import sqlite3
import os
from typing import Any

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".data", "ledger.db")

def get_latest_delayed_prices(ticker: str | None = None) -> list[dict[str, Any]]:
    """
    Queries the local SQLite database for the latest prices for tracked tickers.
    Optionally filters by a specific ticker.
    Returns a list of price records.
    """
    if not os.path.exists(DB_PATH):
        return [{"error": "Database not found", "path": DB_PATH}]

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if ticker:
            cursor.execute('''
                SELECT ticker, price, change_pct, timestamp 
                FROM price_history 
                WHERE ticker = ?
                ORDER BY rowid DESC
                LIMIT 1
            ''', (ticker,))
        else:
            # Get latest price for each distinct ticker
            cursor.execute('''
                SELECT ticker, price, change_pct, timestamp 
                FROM price_history 
                WHERE rowid IN (
                    SELECT MAX(rowid) 
                    FROM price_history 
                    GROUP BY ticker
                )
            ''')
        rows = cursor.fetchall()
        return [
            {"ticker": row[0], "price": row[1], "change_pct": row[2], "timestamp": row[3]}
            for row in rows
        ]
    finally:
        conn.close()
