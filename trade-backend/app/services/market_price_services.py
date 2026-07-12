import sqlite3

from app.repositories.market_price_repository import (
    delete_market_price,
    insert_market_price,
    select_market_prices,
)


def getRevenue(open_price, close_price):
    return close_price - open_price;


def create_market_price(symbol, open_price, high_price, close_price):
    try:
        insert_market_price(symbol, open_price, high_price, close_price)
    except sqlite3.IntegrityError as exc:
        raise ValueError(str(exc)) from exc


def list_market_prices(symbol=None):
    return select_market_prices(symbol)


def remove_market_price(symbol):
    deleted = delete_market_price(symbol)
    if deleted == 0:
        raise LookupError(f"symbol '{symbol}' not found")