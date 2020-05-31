from aiogram import Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware

from i17obot.models import User


class UserMiddleware(BaseMiddleware):
    async def setup_user(self, data: dict, telegram_user: types.User, chat: types.Chat):
        user = await User.get_or_create(telegram_user, chat)

        if chat.type == "private" != user.chat_type:
            user.chat_type = chat.type
            await user.update()

        data["user"] = user

    async def on_pre_process_message(self, message: types.Message, data: dict, *args):
        await self.setup_user(data, message.from_user, message.chat)

    async def on_pre_process_callback_query(self, query: types.CallbackQuery, data: dict):
        await self.setup_user(data, query.from_user, query.message.chat)


def setup(dispatcher: Dispatcher):
    dispatcher.middleware.setup(UserMiddleware())
