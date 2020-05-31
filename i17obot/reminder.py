import asyncio
import logging
from unittest.mock import Mock

import sentry_sdk
from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from sentry_sdk.integrations.logging import LoggingIntegration

from i17obot import bot, config
from i17obot.database import get_users_with_reminder_on
from i17obot.handlers.translate import translate
from i17obot.models import User

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def setup_sentry():
    if not config.SENTRY_DSN:
        return

    # All of this is already happening by default!
    sentry_logging = LoggingIntegration(
        level=logging.INFO,  # Capture info and above as breadcrumbs
        event_level=logging.ERROR,  # Send errors as events
    )
    sentry_sdk.init(dsn=config.SENTRY_DSN, integrations=[sentry_logging])


async def reminder(user_id):
    user = await User.get(user_id)
    print("Reminding user:", user.id)
    try:
        await bot.send_message(user.id, "⏰ *Lembrete!*", parse_mode="markdown")
    except BotBlocked:
        logger.warning("i17obot blocked by user. userid=%r", user.id)
        return

    # Mock is needed because the handler `translate_at_transifex`
    # expects a Message object that contains chat.id attribuites.
    mock = Mock(spec=types.Message)
    mock.chat.id = user.id
    mock.from_user.id = user.id
    await translate(mock, user)
    print("Reminder sent to:", user.id)


async def reminder_all_users(users):
    setup_sentry()
    print("Running reminder_all_users task")
    if not users:
        users = [user["id"] for user in await get_users_with_reminder_on()]
    print("Users to remind:", len(users))

    tasks = [reminder(user) for user in users]
    print("Users with reminter set on:", len(tasks))

    results = await asyncio.gather(*tasks, return_exceptions=True)
    for result in results:
        if isinstance(result, Exception):
            logger.exception("Error while reminding user. exception=%r", result)
