from pydantic import BaseModel, root_validator
from decimal import Decimal


class Position(BaseModel):
    description: str
    size: int
    market_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    pnl: Decimal = Decimal('0.0')

    @root_validator()
    def calculate_pnl(cls, values):
        values['pnl'] = values['realized_pnl'] + values['unrealized_pnl']

        return values
