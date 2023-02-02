from pydantic import BaseModel
from decimal import Decimal


class Position(BaseModel):
    description: str
    size: int
    market_price: Decimal
    market_value: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
