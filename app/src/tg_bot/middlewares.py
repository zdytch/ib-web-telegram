from aiogram import Dispatcher
from aiogram.types import Message
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.dispatcher.handler import CancelHandler
from settings import TELEGRAM_USER_ID


def setup_middlewares(dp: Dispatcher):
    dp.middleware.setup(AccessMiddleware(TELEGRAM_USER_ID))


class AccessMiddleware(BaseMiddleware):
    def __init__(self, access_id: int):
        self.access_id: int = access_id

        super().__init__()

    async def on_process_message(self, message: Message, _):
        if message.from_user.id != self.access_id:
            await message.answer('Access Denied')

            raise CancelHandler()
