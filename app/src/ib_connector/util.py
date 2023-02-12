from schemas import Position, Order, Side, OrderStatus, OrderType
from decimal import Decimal


def positions_from_ib(ib_positions: list[dict]) -> list[Position]:
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


def order_from_ib(ib_order: dict) -> Order:
    fill_size, size = ib_order['size_and_fills'].split('/')
    limit_price = Decimal(p) if (p := ib_order.get('price')) else Decimal('0.0')
    stop_price = Decimal(p) if (p := ib_order.get('stop_price')) else Decimal('0.0')
    price = limit_price or stop_price

    return Order(
        id=ib_order['order_id'],
        symbol=ib_order['symbol'],
        size=size,
        fill_size=fill_size,
        side=side_from_ib(ib_order['side']),
        type=order_type_from_ib(ib_order['order_type']),
        status=order_status_from_ib(ib_order['order_status']),
        price=price,
    )


def orders_from_ib(ib_orders: list[dict], statuses: tuple[OrderStatus]) -> list[Order]:
    orders = []

    for ib_order in ib_orders:
        if (status := order_status_from_ib(ib_order['status'])) in statuses:
            fill_size = int(ib_order['filledQuantity'])
            remaining_size = int(ib_order['remainingQuantity'])
            size = fill_size + remaining_size
            price = Decimal(p) if (p := ib_order.get('price')) else Decimal('0.0')

            order = Order(
                id=ib_order['orderId'],
                symbol=ib_order['ticker'],
                size=size,
                fill_size=fill_size,
                side=side_from_ib(ib_order['side']),
                status=status,
                type=order_type_from_ib(ib_order['orderType']),
                price=price,
            )
            orders.append(order)

    return orders


def side_from_ib(ib_side: str) -> Side:
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


def order_status_from_ib(ib_status: str) -> OrderStatus:
    try:
        status = OrderStatus(ib_status.upper())

    except ValueError:
        if ib_status in ('PendingSubmit', 'PreSubmitted'):
            status = OrderStatus.SUBMITTED

        elif ib_status in ('PendingCancel', 'Inactive'):
            status = OrderStatus.CANCELLED

        else:
            raise ValueError(
                f'Cannot recognize order status, unknown value: {ib_status}'
            )

    return status


def order_type_from_ib(ib_type: str) -> OrderType:
    try:
        type = OrderType(ib_type.upper())

    except ValueError:
        if ib_type == 'STP':
            type = OrderType.STOP

        else:
            raise ValueError(f'Cannot recognize order type, unknown value: {ib_type}')

    return type
