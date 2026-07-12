import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[3] / "data" / "market_stock.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def insert_market_price(symbol, open_price, high_price, close_price):
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO market_price (symbol, open_price, high_price, close_price)
            VALUES (?, ?, ?, ?)
            """,
            (symbol, open_price, high_price, close_price),
        )


def select_market_prices(symbol=None):
    with get_connection() as conn:
        if symbol is None:
            rows = conn.execute("SELECT * FROM market_price").fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM market_price WHERE symbol = ?", (symbol,)
            ).fetchall()
        return [dict(row) for row in rows]


def delete_market_price(symbol):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM market_price WHERE symbol = ?", (symbol,)
        )
        return cursor.rowcount
