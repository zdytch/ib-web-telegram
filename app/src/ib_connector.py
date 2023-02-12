from asyncio import sleep
from httpx import AsyncClient, HTTPError, codes
from schemas import Position, Order, Side, OrderStatus, OrderType
from decimal import Decimal
from loguru import logger
from settings import IB_URL_BASE


class IBConnectorError(Exception):
    pass


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
    '''
    https://interactivebrokers.github.io/cpwebapi/use-cases
    Similarly to market data snapshots, order updates retrieved via the
    /iserver/account/orders endpoints will require two calls to the server before
    meaningful data is returned. The first call creates a subscription to the order
    updates, with the second call returning the actual data. Please allow up to 5 seconds
    for the order updates subscription to be created before making the second call.
    '''

    data = await _send_request(
        'GET',
        '/iserver/account/orders',
        {'Filters': 'pending_submit,pre_submitted,submitted'},
    )

    if isinstance(data, dict) and not data['snapshot']:
        await sleep(1)

        # TODO Recursion
        data = await get_orders()

    if isinstance(data, dict):
        return _orders_from_ib(data['orders'])

    else:
        raise IBConnectorError(f'Cannot get order list, wrong value returned: {data}')


async def get_order(id: int) -> Order | None:
    data = await _send_request('GET', f'/iserver/account/order/status/{id}')

    if isinstance(data, dict):
        return _order_from_ib(data) if not data.get('error') else None

    else:
        raise IBConnectorError(f'Cannot get order, wrong value returned: {data}')


async def cancel_order(id: int) -> None:
    '''
    https://interactivebrokers.github.io/cpwebapi/endpoints
    Cancels an open order. Must call /iserver/accounts endpoint prior to cancelling an order.
    Use /iservers/account/orders endpoint to review open-order(s) and get latest order status.
    '''
    await _send_request('GET', '/iserver/accounts')

    await _send_request('DELETE', f'/iserver/account/DU1692823/order/{id}')


async def cancel_all_orders() -> None:
    orders = await get_orders()

    for order in orders:
        await cancel_order(order.id)


async def _send_request(method: str, endpoint: str, params: dict = {}) -> dict | list:
    try:
        async with AsyncClient(verify=False) as client:
            r = await client.request(method, f'{IB_URL_BASE}{endpoint}', params=params)

        return r.json()

    except HTTPError as error:
        logger.error(error)

        raise IBConnectorError()


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
        price = Decimal(p) if (p := ib_order.get('price')) else Decimal('0.0')

        order = Order(
            id=ib_order['orderId'],
            symbol=ib_order['ticker'],
            size=size,
            fill_size=fill_size,
            side=_side_from_ib(ib_order['side']),
            status=_order_status_from_ib(ib_order['status']),
            type=_order_type_from_ib(ib_order['orderType']),
            price=price,
        )
        orders.append(order)

    return orders


def _side_from_ib(ib_side: str) -> Side:
    try:
        side = Side(ib_side.upper())

    except ValueError:
        if ib_side == 'B':
            side = Side.BUY

        elif ib_side == 'S':
            side = Side.SELL

        else:
            raise ValueError(f'Cannot recognize side, unknown value: {ib_side}')

    return side


def _order_status_from_ib(ib_status: str) -> OrderStatus:
    try:
        status = OrderStatus(ib_status.upper())

    except ValueError:
        if ib_status in ('PendingSubmit', 'PreSubmitted'):
            status = OrderStatus.SUBMITTED

        else:
            raise ValueError(
                f'Cannot recognize order status, unknown value: {ib_status}'
            )

    return status


def _order_type_from_ib(ib_type: str) -> OrderType:
    try:
        type = OrderType(ib_type.upper())

    except ValueError:
        if ib_type == 'STP':
            type = OrderType.STOP

        else:
            raise ValueError(f'Cannot recognize order type, unknown value: {ib_type}')

    return type
