import asyncio
import logging
from unittest.mock import Mock

from aiogram import types
from aiogram.utils.exceptions import BotBlocked

from i17obot import bot
from i17obot.database import get_users_with_reminder_on
from i17obot.handlers.translate import translate

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


async def reminder(user_id):
    print("Reminding user:", user_id)
    try:
        await bot.send_message(user_id, "⏰ *Lembrete!*", parse_mode="markdown")
    except BotBlocked:
        logger.warning("i17obot blocked by user. userid=%r", user_id)
        return

    # Mock is needed because the handler `translate_at_transifex`
    # expects a Message object that contains chat.id attribuites.
    mock = Mock(spec=types.Message)
    mock.chat.id = user_id
    mock.from_user.id = user_id
    await translate(mock)
    print("Reminder sent to:", user_id)


async def reminder_all_users():
    print("Running reminder_all_users task")
    users = await get_users_with_reminder_on()
    print("Users to reminde:", len(users))
    tasks = [reminder(user["id"]) for user in users]
    print("Users with reminter set on:", len(tasks))
    await asyncio.gather(*tasks)
