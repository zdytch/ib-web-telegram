from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    Message,
    CallbackQuery,
    KeyboardButton,
    ReplyKeyboardMarkup,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
)
from ib_connector import get_positions, get_orders
from templates import render_position, render_order
from schemas import Position, Order
from datetime import datetime, timedelta
from settings import TELEGRAM_TOKEN

if not TELEGRAM_TOKEN:
    exit()

bot = Bot(token=TELEGRAM_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# TODO: Use db
_positions: list[Position] = []
_positions_expiration: datetime = datetime.now()
_orders: list[Order] = []
_orders_expiration: datetime = datetime.now()


def run_tg_bot() -> None:
    executor.start_polling(dp, skip_updates=True)  # on_startup


@dp.message_handler(commands=['start'])
async def start(message: Message):
    kb = _main_menu_keyboard()
    await message.answer(f'Welcome!', reply_markup=kb)


@dp.message_handler(commands=['positions'])
async def positions(message: Message):
    if positions := await _get_position_list():
        kb = _position_list_keyboard(positions)
        await message.answer(f'Total Positions: {len(positions)}', reply_markup=kb)

    else:
        await message.answer('No positions')


@dp.message_handler(commands=['orders'])
async def orders(message: Message):
    if orders := await _get_order_list():
        kb = _order_list_keyboard(orders)
        await message.answer(f'Total Orders: {len(orders)}', reply_markup=kb)

    else:
        await message.answer('No orders')


@dp.message_handler()
async def unknown_message(message: Message):
    await message.delete()


@dp.callback_query_handler()
async def inline_callback(callback: CallbackQuery):
    if position := await _get_position(callback.data):
        await callback.message.answer(render_position(position))

    elif order := await _get_order(int(callback.data)):
        await callback.message.answer(render_order(order))


async def _get_position_list() -> list[Position]:
    global _positions
    global _position_expiration

    if (now := datetime.now()) >= _positions_expiration:
        _positions.clear()

        if origin_positions := await get_positions():
            _positions = origin_positions
            _position_expiration = now + timedelta(seconds=60)

    return _positions


async def _get_position(description: str) -> Position | None:
    positions = await _get_position_list()

    return next((p for p in positions if p.description == description), None)


async def _get_order_list() -> list[Order]:
    global _orders
    global _orders_expiration

    if (now := datetime.now()) >= _orders_expiration:
        _orders.clear()

        if origin_orders := await get_orders():
            _orders = origin_orders
            _orders_expiration = now + timedelta(seconds=10)

    return _orders


async def _get_order(id: int) -> Order | None:
    orders = await _get_order_list()

    return next((o for o in orders if o.id == id), None)


def _main_menu_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton('/positions'), KeyboardButton('/orders'))

    return keyboard


def _position_list_keyboard(positions: list[Position]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(3, resize_keyboard=True)

    for position in positions:
        icon = '🟢' if position.pnl > 0 else '🔴' if position.pnl < 0 else ''
        button = InlineKeyboardButton(
            f'{icon} {position.description}', callback_data=position.description
        )
        keyboard.insert(button)

    return keyboard


def _order_list_keyboard(orders: list[Order]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(1, resize_keyboard=True)

    for order in orders:
        button = InlineKeyboardButton(order.description, callback_data=str(order.id))
        keyboard.row(button)

    return keyboard
