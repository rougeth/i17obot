from collections import defaultdict

from aiogram import types
from aiogram.utils.text_decorations import markdown_decoration

from i17obot import bot, config, dp
from i17obot.database import get_all_users
from i17obot.models import User
from i17obot.templates import render_template
from i17obot.transifex import translation_stats
from i17obot.utils import message_admins, sum_stats


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


@dp.message_handler(commands=["beta"])
async def beta(message: types.Message):
    user = await User.get(message.from_user.id)
    if user.is_beta:
        await bot.send_message(
            message.chat.id, "You're a *beta* user!", parse_mode="markdown",
        )
        return

    response = await render_template(user.id, "beta_request", user=user)
    await message_admins(response)
    await bot.send_message(
        message.chat.id, "Beta access requested...", parse_mode="markdown",
    )


@dp.message_handler(lambda message: message.text.startswith("/beta_"))
async def beta_access(message: types.Message):
    user_id = int(message.text.replace("/beta_", ""))
    user = await User.get(user_id)
    user.is_beta = True
    await user.update()

    await bot.send_message(
        user.id, "You're a *beta* user!", parse_mode="markdown",
    )
