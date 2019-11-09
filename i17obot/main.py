import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from decouple import config

import handlers
import messages
from telegram import bot
from transifex import random_string, transifex_api
from database import create_user

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcast")


class CreateUserMiddleware(BaseMiddleware):
    cached_user_ids = []

    async def on_pre_process_message(self, message: types.Message, *args):
        if message.from_user.id not in self.cached_user_ids:
            await create_user(message.from_user, chat_type=message.chat.type)
            self.cached_user_ids.append(message.from_user.id)


if __name__ == "__main__":
    dp = Dispatcher(bot, loop=asyncio.get_event_loop())
    dp.middleware.setup(CreateUserMiddleware())

    dp.register_message_handler(handlers.start, commands=["start", "help", "ajuda"])
    dp.register_message_handler(
        handlers.translate_at_transifex, commands=["translate", "traduzir"]
    )
    dp.register_message_handler(handlers.reminder, commands=["reminder", "lembrete"])

    executor.start_polling(dp, skip_updates=True)
