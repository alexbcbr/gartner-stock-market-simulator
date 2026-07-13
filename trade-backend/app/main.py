import logging

from fastapi import FastAPI

from app.utils.logging import setup_logging
from app.routers import market_price, revenue, trade

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

app.include_router(revenue.router)
app.include_router(market_price.router)
app.include_router(trade.router)


@app.get("/")
def read_root():
    logger.info("Initialize API")
    return {"message": "Hello from trade-backend!"}
