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


class Order(BaseModel):
    description: str = ''
    symbol: str
    id: int
    size: int
    fill_size: int
    type: str
    side: str
    status: str
    price: Decimal

    @root_validator()
    def generate_description(cls, values):
        price = price if (price := values['price']) else ''

        values['description'] = (
            f'{values["symbol"]} '
            f'{values["side"]} '
            f'{values["size"]} '
            f'{values["type"]} '
            f'{price}'
        )

        return values
