from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from aiogram.utils.callback_data import CallbackData
from schemas import Position, Order


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton('/positions'), KeyboardButton('/orders'))

    return keyboard


def position_list_keyboard(
    positions: list[Position], callback_data: CallbackData
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1)
    close_all_button = InlineKeyboardButton(
        'Close All Positions',
        callback_data=callback_data.new(id='all', action='delete'),
    )

    for position in positions:
        icon = '⬆️' if position.size > 0 else '⬇️' if position.size < 0 else ''
        size = abs(position.size)
        pnl = f'+{position.pnl}' if position.pnl > 0 else position.pnl

        button = InlineKeyboardButton(
            f'{icon} {size} {position.description} ({pnl})',
            callback_data=callback_data.new(id=position.contract_id, action='view'),
        )
        keyboard.row(button)

    keyboard.row(close_all_button)

    return keyboard


def position_view_keyboard(
    position: Position, callback_data: CallbackData
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1)
    close_button = InlineKeyboardButton(
        'Close Position',
        callback_data=callback_data.new(id=position.contract_id, action='delete'),
    )
    keyboard.row(close_button)

    return keyboard


def order_list_keyboard(
    orders: list[Order], callback_data: CallbackData
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1)
    cancel_all_button = InlineKeyboardButton(
        'Cancel All Orders',
        callback_data=callback_data.new(id='all', action='delete'),
    )

    for order in orders:
        button = InlineKeyboardButton(
            order.description,
            callback_data=callback_data.new(id=order.id, action='view'),
        )
        keyboard.row(button)

    keyboard.row(cancel_all_button)

    return keyboard


def order_view_keyboard(
    order: Order, callback_data: CallbackData
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1)
    close_button = InlineKeyboardButton(
        'Cancel Order',
        callback_data=callback_data.new(id=order.id, action='delete'),
    )
    keyboard.row(close_button)

    return keyboard
