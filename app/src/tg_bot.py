from aiogram import Bot, Dispatcher, executor
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from ib_connector import get_positions
from schemas import Position
from datetime import datetime, timedelta
from settings import TELEGRAM_TOKEN

if not TELEGRAM_TOKEN:
    exit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

# TODO: Use db
_positions: list[Position] = []
_position_expiration: datetime = datetime.now()


def run_tg_bot() -> None:
    executor.start_polling(dp, skip_updates=True)  # on_startup


@dp.message_handler(commands=['start', 'help'])
async def start(message: Message):
    await message.answer("Start!")


@dp.message_handler(commands=['positions'])
async def position_list(message: Message):
    if positions := await _get_position_list():
        kb = _position_keyboard(positions)

        await message.answer(f'Total Positions: {len(positions)}', reply_markup=kb)

    else:
        await message.answer('No positions')


@dp.message_handler()
async def unknown_message(message: Message):
    await message.delete()


@dp.callback_query_handler()
async def inline_callback(callback: CallbackQuery):
    if position := await _get_position(callback.data):
        await callback.message.answer(f'{position}')


async def _get_position_list() -> list[Position]:
    global _positions
    global _position_expiration

    if (now := datetime.now()) >= _position_expiration:
        _positions.clear()

        if origin_positions := await get_positions():
            _positions = origin_positions
            _position_expiration = now + timedelta(seconds=60)

    return _positions


async def _get_position(description: str) -> Position | None:
    positions = await _get_position_list()

    return next((p for p in positions if p.description == description), None)


def _position_keyboard(positions: list[Position]) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(p.description, callback_data=p.description)
        for p in positions
    ]
    keyboard = InlineKeyboardMarkup(2, resize_keyboard=True)
    keyboard.add(*buttons)

    return keyboard
