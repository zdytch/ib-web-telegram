from aiogram import Bot, Dispatcher, executor, types
from ib_connector import get_positions
from settings import TELEGRAM_TOKEN

if not TELEGRAM_TOKEN:
    exit()

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


def run_tg_bot() -> None:
    executor.start_polling(dp, skip_updates=True)  # on_startup


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer("Start!")


@dp.message_handler(commands=['positions'])
async def view_positions(message: types.Message):
    positions = await get_positions()

    await message.answer(f'{positions}')


@dp.message_handler()
async def unknown(message: types.Message):
    await message.delete()
