from asyncio import sleep
from httpx import AsyncClient, HTTPError, codes
from schemas import Position, Order, OrderStatus
from . import util
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
            positions = util.positions_from_ib(response.json())

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

    data = await _send_request('GET', '/iserver/account/orders')

    if isinstance(data, dict) and not data['snapshot']:
        await sleep(2)

        data = await _send_request('GET', '/iserver/account/orders')

    if isinstance(data, dict):
        return util.orders_from_ib(data['orders'], (OrderStatus.SUBMITTED,))

    else:
        raise IBConnectorError(f'Cannot get order list, wrong value returned: {data}')


async def get_order(id: int) -> Order | None:
    data = await _send_request('GET', f'/iserver/account/order/status/{id}')

    if isinstance(data, dict):
        return util.order_from_ib(data) if not data.get('error') else None

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
