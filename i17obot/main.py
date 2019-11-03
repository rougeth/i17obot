import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from decouple import config

import messages
from middlewares import UserDatabaseMiddleware
from transifex import transifex_api, random_string
from telegram import bot
from database import database
from handlers import review


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcast")


def expected_state(state: str):
    def f(message: types.Message):
        user = database.get(message.from_user.id)
        if not user:
            raise Exception("User not found")

        valid_state = user.state == state
        if not valid_state:
            logger.error(
                "Unexpected state, user_state=%s, expected_state=%s", user.state, state
            )
        return valid_state

    return f

if __name__ == "__main__":
    dp = Dispatcher(bot, loop=asyncio.get_event_loop())
    dp.middleware.setup(UserDatabaseMiddleware(database))

    dp.register_message_handler(review.review_start, expected_state("asleep"), commands=["review", "revisar"])
    dp.register_callback_query_handler(review.review, expected_state("reviewing"))
    dp.register_callback_query_handler(review.refine, expected_state("refining"))
    dp.register_message_handler(review.refining, expected_state("refining"))

    executor.start_polling(dp, skip_updates=True)
