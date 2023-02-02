from pydantic import BaseModel
from decimal import Decimal


class Position(BaseModel):
    description: str  # "contractDesc":"AAPL"
    size: int  # "position":100.0
    market_price: Decimal  # "mktPrice":145.8899994,
    market_value: Decimal  # "mktValue":14589.0,
    realized_pnl: Decimal  # "realizedPnl":0.0,
    unrealized_pnl: Decimal  # "unrealizedPnl":399.33,
