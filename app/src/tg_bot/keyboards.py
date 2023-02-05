from aiogram.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from schemas import Position, Order


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton('/positions'), KeyboardButton('/orders'))

    return keyboard


def position_list_keyboard(positions: list[Position]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(3, resize_keyboard=True)

    for position in positions:
        icon = '🟢' if position.pnl > 0 else '🔴' if position.pnl < 0 else ''
        button = InlineKeyboardButton(
            f'{icon} {position.description}', callback_data=position.description
        )
        keyboard.insert(button)

    return keyboard


def order_list_keyboard(orders: list[Order]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1, resize_keyboard=True)

    for order in orders:
        button = InlineKeyboardButton(order.description, callback_data=str(order.id))
        keyboard.row(button)

    return keyboard
