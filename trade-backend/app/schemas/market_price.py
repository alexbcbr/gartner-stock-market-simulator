from pydantic import BaseModel


class MarketPrice(BaseModel):
    symbol: str
    open_price: float
    high_price: float
    close_price: float
