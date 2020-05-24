from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware

from i17obot.database import create_user


class CreateUserMiddleware(BaseMiddleware):
    cached_user_ids = []

    async def on_pre_process_message(self, message: types.Message, *args):
        if message.from_user.id not in self.cached_user_ids:
            await create_user(message.from_user, chat_type=message.chat.type)
            self.cached_user_ids.append(message.from_user.id)


def setup(dispatcher: Dispatcher):
    dispatcher.middleware.setup(CreateUserMiddleware())
