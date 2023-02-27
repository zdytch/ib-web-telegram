from asyncio import sleep
from httpx import AsyncClient, HTTPError
from schemas import Position, Order, SubmitData, OrderStatus, Exchange
from . import util
from loguru import logger
from settings import IB_URL_BASE, IB_ACCOUNT


class IBConnectorError(Exception):
    pass


async def get_positions() -> list[Position]:
    '''
    https://interactivebrokers.github.io/cpwebapi/endpoints
    The endpoint supports paging, page's default size is 30 positions.
    /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint.
    '''
    await _send_request('GET', '/portfolio/accounts')

    ib_positions = await _send_request('GET', f'/portfolio/{IB_ACCOUNT}/positions')

    if not isinstance(ib_positions, list):
        raise IBConnectorError(
            f'Cannot get position list, wrong value returned: {ib_positions}'
        )

    return util.positions_from_ib(ib_positions)


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

    if not isinstance(ib_orders, dict):
        raise IBConnectorError(
            f'Cannot get order list, wrong value returned: {ib_orders}'
        )

    return util.orders_from_ib(ib_orders['orders'], (OrderStatus.SUBMITTED,))


async def get_order(id: int) -> Order | None:
    ib_order = await _send_request('GET', f'/iserver/account/order/status/{id}')

    if not isinstance(ib_order, dict):
        raise IBConnectorError(f'Cannot get order, wrong value returned: {ib_order}')

    return util.order_from_ib(ib_order) if not ib_order.get('error') else None


async def cancel_order(id: int) -> None:
    '''
    https://interactivebrokers.github.io/cpwebapi/endpoints
    Cancels an open order. Must call /iserver/accounts endpoint prior to cancelling an order.
    Use /iservers/account/orders endpoint to review open-order(s) and get latest order status.
    '''
    await _send_request('GET', '/iserver/accounts')

    await _send_request('DELETE', f'/iserver/account/{IB_ACCOUNT}/order/{id}')


async def submit_order(data: SubmitData) -> None:
    ib_data = util.submit_data_to_ib(data)

    await _send_request('POST', f'/iserver/account/{IB_ACCOUNT}/orders', ib_data)


async def get_contract_id(symbol: str, exchange: Exchange) -> int | None:
    ib_stocks = await _send_request('GET', f'/trsrv/stocks?symbols={symbol}')

    if not isinstance(ib_stocks, dict):
        raise IBConnectorError(
            f'Cannot get contract_id, wrong value returned: {ib_stocks}'
        )

    return util.contract_id_from_ib(ib_stocks, symbol, exchange)


async def _send_request(
    method: str, endpoint: str, data: dict | None = None, params: dict | None = None
) -> dict | list:
    try:
        async with AsyncClient(verify=False) as client:
            response = await client.request(
                method, f'{IB_URL_BASE}{endpoint}', json=data, params=params
            )

        json = response.json()

        logger.debug(json)

        return json

    except HTTPError as error:
        logger.error(error)

        raise IBConnectorError()
