import asyncio

from aiogram import Bot, types

from i17obot import config

bot = Bot(token=config.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML,)
