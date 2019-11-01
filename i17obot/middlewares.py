from aiogram import types
from aiogram.dispatcher.middlewares import BaseMiddleware

from states import User


class UserDatabaseMiddleware(BaseMiddleware):
    def __init__(self, database, *args, **kwargs):
        self.database = database
        super().__init__(*args, **kwargs)

    async def on_pre_process_message(self, message: types.Message, *args):
        user_id = message.from_user.id
        if user_id not in self.database:
            self.database[user_id] = User()
