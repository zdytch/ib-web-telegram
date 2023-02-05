from aiogram import Bot, Dispatcher, executor, types
from . import handlers
from settings import TELEGRAM_TOKEN


def run_tg_bot() -> None:
    if not TELEGRAM_TOKEN:
        exit()

    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    message_handlers = {
        'start': handlers.start,
        # TODO "help": handlers.help_,
        'positions': handlers.positions,
        'orders': handlers.orders,
        '': handlers.unknown_message,
    }
    for command, handler in message_handlers.items():
        dp.register_message_handler(handler, commands=[command])

    dp.register_callback_query_handler(handlers.inline_callback)

    executor.start_polling(dp, skip_updates=True)  # TODO on_startup
