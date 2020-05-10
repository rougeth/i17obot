import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from aiogram.dispatcher.middlewares import BaseMiddleware
from decouple import config

import config
import handlers
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

    dp.register_message_handler(
        handlers.start, commands=["start", "help", "ajuda", "ayuda"]
    )

    dp.register_message_handler(handlers.language, commands=["language"])
    dp.register_callback_query_handler(
        handlers.set_language, lambda query: query.data in config.AVAILABLE_LANGUAGES,
    )

    dp.register_message_handler(handlers.projects, commands=["projects", "project"])
    dp.register_callback_query_handler(
        handlers.set_project, lambda query: query.data in config.AVAILABLE_PROJECTS,
    )

    dp.register_message_handler(
        handlers.translate_at_transifex, commands=["translate", "traduzir", "traducir"]
    )
    dp.register_message_handler(
        handlers.reminder, commands=["reminder", "lembrete", "recordatorio"]
    )
    dp.register_message_handler(handlers.status, commands=["status"])
    dp.register_message_handler(handlers.links, commands=["links", "link"])

    dp.register_message_handler(handlers.tutorial_1, commands=["tutorial"])
    dp.register_callback_query_handler(handlers.tutorial_1, text="tutorial_1")
    dp.register_callback_query_handler(handlers.tutorial_2, text="tutorial_2")
    dp.register_callback_query_handler(handlers.tutorial_3, text="tutorial_3")

    executor.start_polling(dp, skip_updates=True)
