from aiogram import types
from aiogram.utils.markdown import escape_md, quote_html
from decouple import Csv, config

import messages
from telegram import bot
from transifex import random_string, transifex_string_url
from database import get_all_users, toggle_reminder
from utils import docsurl

ADMINS = config("ADMINS", cast=Csv(int))


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

    docspath = escape_md("/".join(resource.split("--")))
    docsurl = f"https://docs.python.org/{docspath}.html"

    response = messages.translate_at_transifex.format(
        source=string["source_string"],
        transifex_url=string_url,
        docsurl=docsurl,
    )

    response = quote_html(response)

    await bot.send_message(
        message.chat.id, response, disable_web_page_preview=True, parse_mode="markdown",
    )


async def status(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    users = await get_all_users()

    await bot.send_message(
        message.chat.id,
        messages.status.format(
            users=len(users),
            reminders=len([user for user in users if user.get("reminder_set")]),
        ),
        parse_mode="markdown",
    )
