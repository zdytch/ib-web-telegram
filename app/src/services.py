from schemas import Position, Order
import ib_connector


async def get_position_list() -> list[Position]:
    return await ib_connector.get_positions()


async def get_position(cotract_id: int) -> Position | None:
    return await ib_connector.get_position(cotract_id)


async def get_order_list() -> list[Order]:
    return await ib_connector.get_orders()


async def get_order(id: int) -> Order | None:
    return await ib_connector.get_order(id)
