import logging
import os

from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.markdown import escape_md, quote_html
from decouple import Csv, config

import messages
from telegram import bot
from transifex import random_string, transifex_string_url
from database import get_all_users, toggle_reminder
from utils import docsurl

ADMINS = config("ADMINS", cast=Csv(int))

BASE_DIR = os.path.dirname(__file__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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


async def status(message: types.Message):
    if message.from_user.id not in ADMINS:
        return

    users = await get_all_users()
    users = [user for user in users if user.get("chat_type") == "private"]

    await bot.send_message(
        message.chat.id,
        messages.status.format(
            users=len(users),
            reminders=len([user for user in users if user.get("reminder_set")]),
        ),
        parse_mode="markdown",
    )


async def links(message: types.Message):
    await bot.send_message(
        message.chat.id,
        messages.links,
        parse_mode="markdown",
        disable_web_page_preview=True,
    )


async def tutorial_1(message: types.Message):
    if isinstance(message, types.CallbackQuery):
        await tutorial_callback_query(
            message,
            message=messages.tutorial_part_1,
            media=os.path.join(BASE_DIR, "data/i17obot-1.mp4"),
            keyboards=[("<< Anterior", "tutorial_2")],
        )
        return

    await types.ChatActions.upload_video()

    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.row(
        types.InlineKeyboardButton("Próximo >>", callback_data="tutorial_2"),
    )

    await bot.send_animation(
        chat_id=message.chat.id,
        animation=types.InputFile(os.path.join(BASE_DIR, "data/i17obot-2.mp4")),
        caption=messages.tutorial_part_1,
        parse_mode="markdown",
        reply_markup=keyboard_markup,
    )


async def tutorial_2(query: types.CallbackQuery):
    keyboards = (
        ("<< Anterior", "tutorial_1"),
        ("Próximo >>", "tutorial_3"),
    )
    await tutorial_callback_query(
        query,
        message=messages.tutorial_part_2,
        media=os.path.join(BASE_DIR, "data/i17obot-2.mp4"),
        keyboards=keyboards,
    )


async def tutorial_3(query: types.CallbackQuery):
    keyboards = (("<< Anterior", "tutorial_2"),)
    await tutorial_callback_query(
        query,
        message=messages.tutorial_part_3,
        media=os.path.join(BASE_DIR, "data/dog_seriously_working.mp4"),
        keyboards=[("<< Anterior", "tutorial_2")],
    )


async def tutorial_callback_query(query, message, media, keyboards):
    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.row(
        *[
            types.InlineKeyboardButton(label, callback_data=callback_data)
            for label, callback_data in keyboards
        ]
    )
    animation = types.InputMediaAnimation(
        media=types.InputFile(media), caption=message, parse_mode="markdown",
    )

    await types.ChatActions.upload_video()
    await bot.edit_message_media(
        media=animation,
        chat_id=query.message.chat.id,
        message_id=query.message.message_id,
        reply_markup=keyboard_markup,
    )
