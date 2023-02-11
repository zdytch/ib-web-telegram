from httpx import AsyncClient, HTTPError, codes
from schemas import Position, Order, Side, OrderStatus, OrderType
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


async def get_position(contract_id: int) -> Position | None:
    return next(
        (p for p in await get_positions() if p.contract_id == contract_id),
        None,
    )


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


async def get_order(id: int) -> Order | None:
    order = None

    try:
        async with AsyncClient(verify=False) as client:
            # TODO: Investigate
            await client.get(f'{IB_URL_BASE}/portfolio/accounts')

            response = await client.get(
                f'{IB_URL_BASE}/iserver/account/order/status/{id}'
            )

        if response.status_code == codes.OK:
            order = _order_from_ib(response.json())

    except HTTPError as error:
        logger.debug(error)

    return order


def _positions_from_ib(ib_positions: list[dict]) -> list[Position]:
    positions = []

    for ib_position in ib_positions:
        position = Position(
            contract_id=ib_position['conid'],
            description=ib_position['contractDesc'],
            size=int(ib_position['position']),
            market_price=Decimal(str(round(ib_position['mktPrice'], 2))),
            market_value=Decimal(str(round(ib_position['mktValue'], 2))),
            realized_pnl=Decimal(str(round(ib_position['realizedPnl'], 2))),
            unrealized_pnl=Decimal(str(round(ib_position['unrealizedPnl'], 2))),
        )
        positions.append(position)

    return positions


def _order_from_ib(ib_order: dict) -> Order:
    fill_size, size = ib_order['size_and_fills'].split('/')
    limit_price = Decimal(p) if (p := ib_order.get('price')) else Decimal('0.0')
    stop_price = Decimal(p) if (p := ib_order.get('stop_price')) else Decimal('0.0')
    price = limit_price or stop_price

    return Order(
        id=ib_order['order_id'],
        symbol=ib_order['symbol'],
        size=size,
        fill_size=fill_size,
        side=_side_from_ib(ib_order['side']),
        type=_order_type_from_ib(ib_order['order_type']),
        status=_order_status_from_ib(ib_order['order_status']),
        price=price,
    )


def _orders_from_ib(ib_orders: list[dict]) -> list[Order]:
    orders = []

    for ib_order in ib_orders:
        fill_size = int(ib_order['filledQuantity'])
        remaining_size = int(ib_order['remainingQuantity'])
        size = fill_size + remaining_size
        price = Decimal(price) if (price := ib_order.get('price')) else Decimal('0.0')

        order = Order(
            id=ib_order['orderId'],
            symbol=ib_order['ticker'],
            size=size,
            fill_size=fill_size,
            side=Side(ib_order['side']),
            status=_order_status_from_ib(ib_order['status']),
            type=_order_type_from_ib(ib_order['orderType']),
            price=price,
        )
        orders.append(order)

    return orders


def _side_from_ib(ib_side: str) -> Side:
    if ib_side == 'B':
        status = Side.BUY

    elif ib_side == 'S':
        status = Side.SELL

    else:
        raise ValueError(f'Cannot recognize side, unknown value: {ib_side}')

    return status


def _order_status_from_ib(ib_status: str) -> OrderStatus:
    if ib_status in ('PendingSubmit', 'PreSubmitted', 'Submitted'):
        status = OrderStatus.SUBMITTED

    elif ib_status == 'Cancelled':
        status = OrderStatus.CANCELLED

    else:
        raise ValueError(f'Cannot recognize order status, unknown value: {ib_status}')

    return status


def _order_type_from_ib(ib_type: str) -> OrderType:
    if ib_type in ('Limit', 'LIMIT'):
        type = OrderType.LIMIT

    elif ib_type in ('Stop', 'STP'):
        type = OrderType.STOP

    elif ib_type in ('Market', 'MARKET'):
        type = OrderType.MARKET

    else:
        raise ValueError(f'Cannot recognize order type, unknown value: {ib_type}')

    return type
