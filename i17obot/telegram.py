import asyncio

from aiogram import Bot, types
from decouple import config


bot = Bot(
    token=config("TELEGRAM_TOKEN"),
    loop=asyncio.get_event_loop(),
    parse_mode=types.ParseMode.HTML,
)
