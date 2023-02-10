from aiogram import Bot, Dispatcher, executor, types
from . import handlers
from . import middlewares
from settings import TELEGRAM_TOKEN, TELEGRAM_USER_ID


def run_tg_bot() -> None:
    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    dp.middleware.setup(middlewares.AccessMiddleware(TELEGRAM_USER_ID))

    dp.register_message_handler(handlers.start, commands=['start'])  # TODO 'help'
    dp.register_message_handler(handlers.positions, commands=['positions'])
    dp.register_message_handler(handlers.orders, commands=['orders'])
    dp.register_message_handler(handlers.unknown_message)

    dp.register_callback_query_handler(handlers.inline_callback)

    executor.start_polling(dp, skip_updates=True)  # TODO on_startup
