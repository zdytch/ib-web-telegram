from schemas import Position, Order
from datetime import datetime, timedelta
from ib_connector import get_positions, get_orders


# TODO: Use db
_positions: list[Position] = []
_positions_expiration: datetime = datetime.now()
_orders: list[Order] = []
_orders_expiration: datetime = datetime.now()


async def get_position_list() -> list[Position]:
    global _positions
    global _position_expiration

    if (now := datetime.now()) >= _positions_expiration:
        _positions.clear()

        if origin_positions := await get_positions():
            _positions = origin_positions
            _position_expiration = now + timedelta(seconds=60)

    return _positions


async def get_position(description: str) -> Position | None:
    positions = await get_position_list()

    return next((p for p in positions if p.description == description), None)


async def get_order_list() -> list[Order]:
    global _orders
    global _orders_expiration

    if (now := datetime.now()) >= _orders_expiration:
        _orders.clear()

        if origin_orders := await get_orders():
            _orders = origin_orders
            _orders_expiration = now + timedelta(seconds=10)

    return _orders


async def get_order(id: int) -> Order | None:
    orders = await get_order_list()

    return next((o for o in orders if o.id == id), None)
