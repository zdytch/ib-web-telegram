from aiogram import Bot, Dispatcher, executor, types
from .handlers import setup_handlers
from .middlewares import setup_middlewares
from settings import TELEGRAM_TOKEN


def run_tg_bot() -> None:
    bot = Bot(token=TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
    dp = Dispatcher(bot)

    setup_handlers(dp)

    setup_middlewares(dp)

    executor.start_polling(dp, skip_updates=True)  # TODO on_startup
