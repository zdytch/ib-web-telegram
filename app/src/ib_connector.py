from httpx import AsyncClient, HTTPError, codes
from schemas import Position, Order
from decimal import Decimal
from loguru import logger
from settings import IB_URL_BASE


async def get_positions() -> list[Position]:
    positions = []

    try:
        async with AsyncClient(verify=False) as client:
            # TODO: Investigate
            # /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint
            # https://interactivebrokers.github.io/cpwebapi/endpoints
            await client.get(f'{IB_URL_BASE}/portfolio/accounts')

            response = await client.get(f'{IB_URL_BASE}/portfolio/DU1692823/positions')

        if response.status_code == codes.OK:
            positions = _positions_from_ib(response.json())

    except HTTPError as error:
        logger.debug(error)

    return positions


async def get_orders() -> list[Order]:
    orders = []

    try:
        async with AsyncClient(verify=False) as client:
            # TODO: Investigate
            await client.get(f'{IB_URL_BASE}/portfolio/accounts')

            response = await client.get(f'{IB_URL_BASE}/iserver/account/orders')

        if response.status_code == codes.OK:
            orders = _orders_from_ib(response.json()['orders'])

    except HTTPError as error:
        logger.debug(error)

    return orders


def _positions_from_ib(ib_positions: list[dict]) -> list[Position]:
    positions = []

    for ib_position in ib_positions:
        position = Position(
            description=ib_position['contractDesc'],
            size=int(ib_position['position']),
            market_price=Decimal(str(round(ib_position['mktPrice'], 2))),
            market_value=Decimal(str(round(ib_position['mktValue'], 2))),
            realized_pnl=Decimal(str(round(ib_position['realizedPnl'], 2))),
            unrealized_pnl=Decimal(str(round(ib_position['unrealizedPnl'], 2))),
        )
        positions.append(position)

    return positions


def _orders_from_ib(ib_orders: list[dict]) -> list[Order]:
    orders = []

    for ib_order in ib_orders:
        fill_size = int(ib_order['filledQuantity'])
        remaining_size = int(ib_order['remainingQuantity'])
        size = fill_size + remaining_size
        price = Decimal(price) if (price := ib_order.get('price')) else Decimal('0.0')

        order = Order(
            description=ib_order['orderDesc'],
            id=ib_order['orderId'],
            size=size,
            fill_size=fill_size,
            type=ib_order['orderType'],
            side=ib_order['side'],
            status=ib_order['status'],
            price=price,
        )
        orders.append(order)

    return orders
