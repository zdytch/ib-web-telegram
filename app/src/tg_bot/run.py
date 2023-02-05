from aiogram import Bot, Dispatcher, executor, types
from . import handlers
from settings import TELEGRAM_TOKEN


def run_tg_bot() -> None:
    if not TELEGRAM_TOKEN:
        exit()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    dp.register_message_handler(handlers.start, commands=['start'])  # TODO 'help'
    dp.register_message_handler(handlers.positions, commands=['positions'])
    dp.register_message_handler(handlers.orders, commands=['orders'])
    dp.register_message_handler(handlers.unknown_message)

    dp.register_callback_query_handler(handlers.inline_callback)

    executor.start_polling(dp, skip_updates=True)  # TODO on_startup
