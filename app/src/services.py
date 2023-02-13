from schemas import Position, Order, SubmitData, Side, OrderType
import ib_connector


async def get_position_list() -> list[Position]:
    return await ib_connector.get_positions()


async def get_position(contract_id: int) -> Position | None:
    return await ib_connector.get_position(contract_id)


async def close_position(contract_id: int) -> None:
    if position := await get_position(contract_id):
        side = Side.SELL if position.size > 0 else Side.BUY
        size = abs(position.size)
        data = SubmitData(
            contract_id=contract_id, side=side, size=size, type=OrderType.MARKET
        )

        await ib_connector.submit_order(data)


async def close_all_positions() -> None:
    for position in await get_position_list():
        await close_position(position.contract_id)


async def get_order_list() -> list[Order]:
    return await ib_connector.get_orders()


async def get_order(id: int) -> Order | None:
    return await ib_connector.get_order(id)


async def cancel_order(id: int) -> None:
    await ib_connector.cancel_order(id)


async def cancel_all_orders() -> None:
    for order in await get_order_list():
        await cancel_order(order.id)
