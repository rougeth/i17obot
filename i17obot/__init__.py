import asyncio

import sentry_sdk
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor

from i17obot import config, middlewares

bot = Bot(token=config.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


def run():
    if config.SENTRY_DSN:
        sentry_sdk.init(config.SENTRY_DSN)

    middlewares.setup(dp)
    import i17obot.handlers

    executor.start_polling(dp, skip_updates=True)
