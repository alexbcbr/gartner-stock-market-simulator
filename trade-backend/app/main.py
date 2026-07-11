import logging

from fastapi import FastAPI

from app.utils.logging import setup_logging
from app.services.market_price_services import getRevenue

setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI()

@app.get("/")
def read_root():
    logger.info("Initialize API")
    return {"message": "Hello from trade-backend-py!"}

@app.get("/revenue")
def get_revenue(open_price: float, close_price: float):
    logger.info("select revevue")
    return {"revenue": getRevenue(open_price, close_price)}
