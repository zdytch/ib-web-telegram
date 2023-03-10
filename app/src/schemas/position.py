from pydantic import BaseModel, validator, root_validator
from decimal import Decimal


class Position(BaseModel):
    contract_id: int
    description: str
    size: int
    market_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    pnl: Decimal = Decimal('0.0')

    @validator('size')
    def size_non_zero(cls, value):
        assert value != 0, 'Size cannot be zero'

        return value

    @root_validator()
    def calculate_pnl(cls, values):
        values['pnl'] = values['realized_pnl'] + values['unrealized_pnl']

        return values
