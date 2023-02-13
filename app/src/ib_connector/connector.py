from asyncio import sleep
from httpx import AsyncClient, HTTPError, codes
from schemas import Position, Order, SubmitData, OrderStatus, Exchange
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

    ib_orders = await _send_request('GET', '/iserver/account/orders')

    if isinstance(ib_orders, dict) and not ib_orders['snapshot']:
        await sleep(2)

        ib_orders = await _send_request('GET', '/iserver/account/orders')

    if isinstance(ib_orders, dict):
        return util.orders_from_ib(ib_orders['orders'], (OrderStatus.SUBMITTED,))

    else:
        raise IBConnectorError(
            f'Cannot get order list, wrong value returned: {ib_orders}'
        )


async def get_order(id: int) -> Order | None:
    ib_order = await _send_request('GET', f'/iserver/account/order/status/{id}')

    if isinstance(ib_order, dict):
        return util.order_from_ib(ib_order) if not ib_order.get('error') else None

    else:
        raise IBConnectorError(f'Cannot get order, wrong value returned: {ib_order}')


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


async def submit_order(data: SubmitData) -> None:
    ib_data = util.submit_data_to_ib(data)

    r = await _send_request('POST', '/iserver/account/DU1692823/orders', ib_data)
    logger.debug(r)


async def get_contract_id(symbol: str, exchange: Exchange) -> int | None:
    ib_stocks = await _send_request('GET', f'/trsrv/stocks?symbols={symbol}')

    if isinstance(ib_stocks, dict):
        return util.contract_id_from_ib(ib_stocks, symbol, exchange)

    else:
        raise IBConnectorError(
            f'Cannot get contract_id, wrong value returned: {ib_stocks}'
        )


async def _send_request(
    method: str, endpoint: str, data: dict | None = None, params: dict | None = None
) -> dict | list:
    try:
        async with AsyncClient(verify=False) as client:
            r = await client.request(
                method, f'{IB_URL_BASE}{endpoint}', json=data, params=params
            )

        return r.json()

    except HTTPError as error:
        logger.error(error)

        raise IBConnectorError()
