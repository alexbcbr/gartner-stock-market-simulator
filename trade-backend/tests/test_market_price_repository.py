import sqlite3
from pathlib import Path

import pytest

from app.repositories import market_price_repository as repo

DDL_PATH = Path(__file__).resolve().parents[2] / "ddl" / "market_price.sql"


@pytest.fixture
def db_path(tmp_path, monkeypatch):
    path = tmp_path / "market_stock.db"
    conn = sqlite3.connect(path)
    conn.executescript(DDL_PATH.read_text())
    conn.close()

    monkeypatch.setattr(repo, "DB_PATH", path)
    return path


def test_insert_market_price(db_path):
    repo.insert_market_price("AAPL", 10, 12, 11)

    rows = repo.select_market_prices()
    assert rows == [
        {"symbol": "AAPL", "open_price": 10, "high_price": 12, "close_price": 11}
    ]


def test_insert_market_price_duplicate_symbol_raises(db_path):
    repo.insert_market_price("AAPL", 10, 12, 11)

    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_market_price("AAPL", 20, 22, 21)


def test_insert_market_price_invalid_symbol_raises(db_path):
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_market_price("aapl", 10, 12, 11)


def test_insert_market_price_negative_price_raises(db_path):
    with pytest.raises(sqlite3.IntegrityError):
        repo.insert_market_price("AAPL", -10, 12, 11)


def test_select_market_prices_returns_all(db_path):
    repo.insert_market_price("AAPL", 10, 12, 11)
    repo.insert_market_price("MSFT", 20, 22, 21)

    rows = repo.select_market_prices()

    assert {row["symbol"] for row in rows} == {"AAPL", "MSFT"}


def test_select_market_prices_filters_by_symbol(db_path):
    repo.insert_market_price("AAPL", 10, 12, 11)
    repo.insert_market_price("MSFT", 20, 22, 21)

    rows = repo.select_market_prices("MSFT")

    assert rows == [
        {"symbol": "MSFT", "open_price": 20, "high_price": 22, "close_price": 21}
    ]


def test_select_market_prices_unknown_symbol_returns_empty(db_path):
    assert repo.select_market_prices("ZZZZ") == []


def test_delete_market_price_removes_row(db_path):
    repo.insert_market_price("AAPL", 10, 12, 11)

    deleted = repo.delete_market_price("AAPL")

    assert deleted == 1
    assert repo.select_market_prices() == []


def test_delete_market_price_unknown_symbol_returns_zero(db_path):
    assert repo.delete_market_price("ZZZZ") == 0
