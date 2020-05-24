from aiogram import types

from i17obot import bot, config, dp
from i17obot.database import get_all_users
from i17obot.templates import render_template


@dp.message_handler(commands=["start", "help", "ajuda", "ayuda"])
async def start(message: types.Message):
    await types.ChatActions.typing()

    response = await render_template(
        message.from_user.id, "start", name=message.from_user.first_name
    )
    await bot.send_message(
        message.chat.id, response, disable_web_page_preview=True, parse_mode="markdown",
    )


@dp.message_handler(commands=["status"])
async def status(message: types.Message):
    if message.from_user.id not in config.ADMINS:
        return

    users = await get_all_users()
    users = [user for user in users if user.get("chat_type") == "private"]

    response = await render_template(
        message.from_user.id,
        "status",
        users=len(users),
        reminders=len([user for user in users if user.get("reminder_set")]),
    )

    await bot.send_message(
        message.chat.id, response, parse_mode="markdown",
    )


@dp.message_handler(commands=["link", "links"])
async def links(message: types.Message):
    response = await render_template(message.from_user.id, "links")
    await bot.send_message(
        message.chat.id, response, parse_mode="markdown", disable_web_page_preview=True,
    )
