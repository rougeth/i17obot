from aiogram import types
from aiogram.utils.markdown import quote_html

import messages
from telegram import bot
from transifex import random_string, transifex_string_url
from database import toggle_reminder


async def start(message: types.Message):
    await bot.send_message(
        message.chat.id,
        messages.start.format(name=message.from_user.first_name),
        disable_web_page_preview=True,
        parse_mode="markdown",
    )


async def reminder(message: types.Message):
    if not types.ChatType.is_private(message.chat):
        return
    reminder_set = await toggle_reminder(message.from_user.id)
    if reminder_set:
        await bot.send_message(
            message.chat.id, messages.reminder_on, parse_mode="markdown",
        )
    else:
        await bot.send_message(
            message.chat.id, messages.reminder_off, parse_mode="markdown",
        )


async def translate_at_transifex(message: types.Message):
    resource, string = await random_string(translated=False, max_size=300)
    string_url = transifex_string_url(resource, string["key"])

    response = messages.translate_at_transifex.format(
        source=string["source_string"], transifex_url=string_url
    )
    response = quote_html(response)

    await bot.send_message(
        message.chat.id, response, disable_web_page_preview=True, parse_mode="markdown",
    )
