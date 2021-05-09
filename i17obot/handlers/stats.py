import typing

from aiogram import types

from i17obot import bot, config, dp
from i17obot.database import get_user, toggle_reminder, update_user, bot_stats
from i17obot.models import User
from i17obot.templates import render_template
from i17obot.utils import check_user_state

from .translate import translate


@dp.message_handler(commands=["botstats"])
async def stats(message: types.Message):
    if not types.ChatType.is_private(message.chat):
        return

    data = await bot_stats()
    response = await render_template(
        message.from_user.id,
        "bot_stats",
        users=data["total_users"],
        strings=data["total_strings"],
        strings_last_month=data["total_strings_past_30_days"],
    )

    await bot.send_message(
        message.chat.id, response, parse_mode="markdown",
    )
