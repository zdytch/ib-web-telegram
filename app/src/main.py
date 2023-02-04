from aiogram import Bot, Dispatcher, executor, types
from ib_connector import get_positions
from settings import TELEGRAM_TOKEN

if not TELEGRAM_TOKEN:
    exit()


bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    await message.answer("Start!")


@dp.message_handler(commands=['positions'])
async def view_positions(message: types.Message):
    pos = await get_positions()
    await message.answer(f"{pos}")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
