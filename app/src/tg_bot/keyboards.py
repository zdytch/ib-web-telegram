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
    keyboard = InlineKeyboardMarkup(3, resize_keyboard=True)

    for position in positions:
        icon = '🟢' if position.pnl > 0 else '🔴' if position.pnl < 0 else ''
        button = InlineKeyboardButton(
            f'{icon} {position.description}',
            callback_data=callback_data.new(id=position.contract_id, action='view'),
        )
        keyboard.insert(button)

    return keyboard


def order_list_keyboard(
    orders: list[Order], callback_data: CallbackData
) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1, resize_keyboard=True)

    for order in orders:
        button = InlineKeyboardButton(
            order.description,
            callback_data=callback_data.new(id=order.id, action='view'),
        )
        keyboard.row(button)

    return keyboard
