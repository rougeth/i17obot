import asyncio
import logging
import os

import aiohttp
import sentry_sdk
from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from decouple import config

import config
import handlers
from database import create_user
from telegram import bot
from transifex import random_string, transifex_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcast")


class CreateUserMiddleware(BaseMiddleware):
    cached_user_ids = []

    async def on_pre_process_message(self, message: types.Message, *args):
        if message.from_user.id not in self.cached_user_ids:
            await create_user(message.from_user, chat_type=message.chat.type)
            self.cached_user_ids.append(message.from_user.id)


if __name__ == "__main__":
    if config.SENTRY_DSN:
        sentry_sdk.init(config.SENTRY_DSN)

    dp = Dispatcher(bot, loop=asyncio.get_event_loop())
    dp.middleware.setup(CreateUserMiddleware())

    dp.register_message_handler(
        handlers.start, commands=["start", "help", "ajuda", "ayuda"]
    )
    dp.register_message_handler(
        handlers.translate_at_transifex, commands=["translate", "traduzir", "traducir"]
    )
    dp.register_message_handler(
        handlers.review_translation, commands=["review", "revisar"]
    )
    dp.register_callback_query_handler(
        handlers.confirm_review,
        lambda query: query.data
        in [
            "review-translation-correct",
            "review-translation-incorrect",
            "review-translation-dont-know",
        ],
    )
    dp.register_message_handler(handlers.status, commands=["status"])
    dp.register_message_handler(handlers.links, commands=["links", "link"])

    # Settings
    # ========

    dp.register_message_handler(handlers.settings.language, commands=["language"])
    dp.register_callback_query_handler(
        handlers.settings.set_language,
        lambda query: query.data in config.AVAILABLE_LANGUAGES,
    )
    dp.register_message_handler(
        handlers.settings.projects, commands=["projects", "project"]
    )
    dp.register_callback_query_handler(
        handlers.settings.set_project,
        lambda query: query.data in config.AVAILABLE_PROJECTS,
    )
    dp.register_message_handler(
        handlers.settings.reminder, commands=["reminder", "lembrete", "recordatorio"]
    )

    # Tutorial
    # ========

    dp.register_message_handler(handlers.tutorial.part_1, commands=["tutorial"])
    dp.register_callback_query_handler(handlers.tutorial.part_1, text="tutorial_1")
    dp.register_callback_query_handler(handlers.tutorial.part_2, text="tutorial_2")
    dp.register_callback_query_handler(handlers.tutorial.part_3, text="tutorial_3")

    executor.start_polling(dp, skip_updates=True)
