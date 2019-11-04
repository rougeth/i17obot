import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from decouple import config

import handlers
import messages
from telegram import bot
from transifex import random_string, transifex_api

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcast")


if __name__ == "__main__":
    dp = Dispatcher(bot, loop=asyncio.get_event_loop())

    dp.register_message_handler(handlers.start, commands=["start", "help", "ajuda"])
    dp.register_message_handler(
        handlers.translate_at_transifex, commands=["translate", "traduzir"]
    )

    executor.start_polling(dp, skip_updates=True)
