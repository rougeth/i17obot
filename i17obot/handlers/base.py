from collections import defaultdict

from aiogram import types

from i17obot import bot, config, dp
from i17obot.database import get_all_users
from i17obot.templates import render_template
from i17obot.transifex import translation_stats
from i17obot.utils import sum_stats


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
    total_users = len(users)
    projects = len(config.AVAILABLE_PROJECTS)

    stats = await translation_stats("pt_BR")
    pt_br = sum_stats(stats)
    print(pt_br)

    stats = await translation_stats("es")
    es = sum_stats(stats)
    print(es)

    response = await render_template(
        message.from_user.id, "status", total_users=total_users, pt_br=pt_br, es=es,
    )

    # es = await stats("es")

    await bot.send_message(
        message.chat.id, response, parse_mode="markdown",
    )


@dp.message_handler(commands=["link", "links"])
async def links(message: types.Message):
    response = await render_template(message.from_user.id, "links")
    await bot.send_message(
        message.chat.id, response, parse_mode="markdown", disable_web_page_preview=True,
    )
