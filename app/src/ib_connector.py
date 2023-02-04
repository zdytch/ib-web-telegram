from httpx import AsyncClient, HTTPError, codes
from schemas import Position
from decimal import Decimal
from settings import IB_URL_BASE


async def get_positions() -> list[Position]:
    positions = []

    try:
        async with AsyncClient(verify=False) as client:
            # TODO: Investigate.
            # /portfolio/accounts or /portfolio/subaccounts must be called prior to this endpoint
            # https://interactivebrokers.github.io/cpwebapi/endpoints
            await client.get(f'{IB_URL_BASE}/portfolio/accounts')

            response = await client.get(f'{IB_URL_BASE}/portfolio/DU1692823/positions')

        if response.status_code == codes.OK:
            positions = _positions_from_ib(response.json())

    except HTTPError as error:
        print(error)

    return positions


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
