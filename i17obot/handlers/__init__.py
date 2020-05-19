import logging

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiogram.utils.markdown import quote_html

import config
from database import get_all_users, get_user, update_user
from handlers import settings, tutorial
from telegram import bot
from templates import render_template
from transifex import random_string, review_string, transifex_string_url
from utils import docsurl

__all__ = [
    "links",
    "settings",
    "start",
    "status",
    "translate_at_transifex",
    "tutorial",
    "review_translation",
]

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def start(message: types.Message):
    await types.ChatActions.typing()

    response = await render_template(
        message.from_user.id, "start", name=message.from_user.first_name
    )
    await bot.send_message(
        message.chat.id, response, disable_web_page_preview=True, parse_mode="markdown",
    )


async def translate_at_transifex(message: types.Message):
    user = await get_user(message.from_user.id)
    language = user.get("language_code") or config.DEFAULT_LANGUAGE
    project = user.get("project") or config.DEFAULT_PROJECT

    resource, string = await random_string(
        language, project, translated=False, max_size=300,
    )
    string_url = transifex_string_url(resource, string["key"], language, project)

    response = await render_template(
        message.from_user.id,
        "translate_at_transifex",
        source=string["source_string"],
        transifex_url=string_url,
        docsurl=docsurl(resource).replace("__", "\_\_"),
    )

    response = quote_html(response)
    try:
        await bot.send_message(
            message.chat.id,
            response,
            disable_web_page_preview=True,
            parse_mode="markdown",
        )
    except BotBlocked:
        logger.exception("i17obot blocked by user. userid=%r", message.chat.id)
    except TelegramAPIError:
        logger.exception(
            "Telegram API Error while sending message. message=%r", response
        )


async def review_translation(message: types.Message):
    if message.chat.type != "private":
        return

    user = await get_user(message.from_user.id)
    language = user.get("language_code") or config.DEFAULT_LANGUAGE
    project = user.get("project") or config.DEFAULT_PROJECT

    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.row(
        types.InlineKeyboardButton(
            "✅ Correta", callback_data="review-translation-correct"
        )
    )
    keyboard_markup.row(
        types.InlineKeyboardButton(
            "❌ Incorreta", callback_data="review-translation-incorrect"
        )
    )
    keyboard_markup.row(
        types.InlineKeyboardButton(
            "❔ Não tenho certeza", callback_data="review-translation-dont-know"
        )
    )

    resource, string = await random_string(language, project, translated=True)
    string["project"] = project
    string["language"] = language

    await update_user(message.from_user.id, reviewing_string=string)

    string_url = transifex_string_url(resource, string["key"], language, project)
    response = await render_template(
        message.from_user.id,
        "review_translation",
        source=string["source_string"],
        translation=string["translation"],
        transifex_url=string_url,
        docsurl=docsurl(resource).replace("__", "\_\_"),
    )

    response = quote_html(response)
    try:
        await bot.send_message(
            message.chat.id,
            response,
            disable_web_page_preview=True,
            reply_markup=keyboard_markup,
            parse_mode="markdown",
        )
    except BotBlocked:
        logger.exception("i17obot blocked by user. userid=%r", message.chat.id)
    except TelegramAPIError:
        logger.exception(
            "Telegram API Error while sending message. message=%r", response
        )


async def confirm_review(query: types.CallbackQuery):
    user = await get_user(query.from_user.id)
    string = user["reviewing_string"]
    string_url = transifex_string_url(
        string["resource"], string["key"], string["language"], string["project"]
    )

    if query.data == "review-translation-incorrect":
        response = await render_template(
            query.from_user.id,
            "translation_incorrect",
            name=query.from_user.first_name,
            string_url=string_url,
        )
    elif query.data == "review-translation-correct":
        response = await review_string(
            string["project"],
            string["resource"],
            string["language"],
            string["translation"],
            string["string_hash"],
        )

        response = await render_template(
            query.from_user.id,
            "translation_correct",
            name=query.from_user.first_name,
            string_url=string_url,
        )
    else:
        response = await render_template(
            query.from_user.id, "dont_know_review", name=query.from_user.first_name,
        )

    await update_user(query.from_user.id, reviewing_string=None)
    await bot.edit_message_text(
        response,
        query.message.chat.id,
        query.message.message_id,
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )


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


async def links(message: types.Message):
    response = await render_template(message.from_user.id, "links")
    await bot.send_message(
        message.chat.id, response, parse_mode="markdown", disable_web_page_preview=True,
    )
