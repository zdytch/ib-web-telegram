from pydantic import BaseModel, root_validator
from decimal import Decimal
from enum import Enum


class Side(Enum):
    BUY = 'BUY'
    SELL = 'SELL'


class Exchange(Enum):
    NYSE = 'NYSE'
    NASDAQ = 'NASDAQ'


class OrderStatus(Enum):
    SUBMITTED = 'SUBMITTED'
    FILLED = 'FILLED'
    CANCELLED = 'CANCELLED'


class OrderType(Enum):
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    MARKET = 'MARKET'


class Order(BaseModel):
    id: int
    symbol: str
    size: int
    fill_size: int
    side: Side
    status: OrderStatus
    type: OrderType
    price: Decimal
    description: str = ''

    @root_validator()
    def generate_description(cls, values):
        price = price if (price := values['price']) else ''

        values['description'] = (
            f'{values["symbol"]} '
            f'{values["side"].value} '
            f'{values["size"]} '
            f'{values["type"].value} '
            f'{price}'
        )

        return values


class SubmitData(BaseModel):
    contract_id: int
    side: Side
    size: int
    type: OrderType
    price: Decimal = Decimal('0.0')

    @root_validator()
    def generate_description(cls, values):
        if values['type'] != OrderType.MARKET:
            assert values['price'] != Decimal('0.0')

        return values
