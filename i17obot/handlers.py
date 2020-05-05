import logging
import os
import typing

from aiogram import types
from aiogram.utils.exceptions import BotBlocked
from aiogram.utils.markdown import escape_md, quote_html

import config
from templates import render_template
from telegram import bot
from transifex import random_string, transifex_string_url
from database import get_all_users, get_user, toggle_reminder, update_user
from utils import docsurl


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


async def language(message: types.Message):
    await types.ChatActions.typing()
    keyboard_markup = types.InlineKeyboardMarkup()
    for code, language in config.AVAILABLE_LANGUAGES.items():
        keyboard_markup.row(types.InlineKeyboardButton(language, callback_data=code))

    await bot.send_message(
        message.chat.id,
        "Translate from English to which language?",
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=keyboard_markup,
    )


async def set_language(query: types.CallbackQuery):
    await types.ChatActions.typing()
    await update_user(query.from_user.id, language_code=query.data)

    # TODO: Find a better way to translate the messages the bot sends
    if query.data == "es":
        template = "Idioma elegido: *{}*.\nUtilice el comando /language para cambiarlo."
    elif query.data == "pt_BR":
        template = "Idioma escolhido: *{}*.\nUse o comando /language para mudar."

    await bot.edit_message_text(
        template.format(config.AVAILABLE_LANGUAGES[query.data]),
        query.message.chat.id,
        query.message.message_id,
        parse_mode="Markdown",
    )


async def projects(message: types.Message):
    await types.ChatActions.typing()
    user = await get_user(message.from_user.id)
    project = user.get("project", "")

    if project:
        template = await render_template(user["id"], "list_projects", project=project)
    else:
        template = await render_template(user["id"], "list_projects_start")

    keyboard_markup = types.InlineKeyboardMarkup()
    for code, project in config.AVAILABLE_PROJECTS.items():
        if code not in project:
            keyboard_markup.row(types.InlineKeyboardButton(project, callback_data=code))

    await bot.send_message(
        message.chat.id,
        template,
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=keyboard_markup,
    )


async def set_project(query: types.CallbackQuery):
    await types.ChatActions.typing()
    user = await get_user(query.from_user.id)
    await update_user(query.from_user.id, project=query.data)

    template = await render_template(user["id"], "selected_project", project=query.data)

    await bot.edit_message_text(
        template,
        query.message.chat.id,
        query.message.message_id,
        parse_mode="Markdown",
    )


async def reminder(message: types.Message):
    if not types.ChatType.is_private(message.chat):
        return

    reminder_set = await toggle_reminder(message.from_user.id)

    template_name = "reminder_on" if reminder_set else "reminder_off"
    response = await render_template(message.from_user.id, template_name)

    await bot.send_message(
        message.chat.id, response, parse_mode="markdown",
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


async def tutorial_1(message: types.Message):
    if isinstance(message, types.CallbackQuery):
        response = await render_template(message.from_user.id, "tutorial_part_1")
        await tutorial_callback_query(
            message,
            response,
            media=os.path.join(config.BASE_DIR, "data/i17obot-1.mp4"),
            keyboards=[("Próximo >>", "tutorial_2")],
        )
        return

    await types.ChatActions.upload_video()

    keyboard_markup = types.InlineKeyboardMarkup()
    keyboard_markup.row(
        types.InlineKeyboardButton("Próximo >>", callback_data="tutorial_2"),
    )

    response = await render_template(message.from_user.id, "tutorial_part_1")

    await bot.send_animation(
        chat_id=message.chat.id,
        animation=types.InputFile(os.path.join(config.BASE_DIR, "data/i17obot-2.mp4")),
        caption=response,
        parse_mode="markdown",
        reply_markup=keyboard_markup,
    )


async def tutorial_2(query: types.CallbackQuery):
    keyboards = (
        ("<< Anterior", "tutorial_1"),
        ("Próximo >>", "tutorial_3"),
    )
    response = await render_template(query.from_user.id, "tutorial_part_2")

    await tutorial_callback_query(
        query,
        message=response,
        media=os.path.join(config.BASE_DIR, "data/i17obot-2.mp4"),
        keyboards=keyboards,
    )


async def tutorial_3(query: types.CallbackQuery):
    keyboards = (("<< Anterior", "tutorial_2"),)
    response = await render_template(query.from_user.id, "tutorial_part_3")
    await tutorial_callback_query(
        query,
        message=response,
        media=os.path.join(config.BASE_DIR, "data/dog_seriously_working.mp4"),
        keyboards=[("<< Anterior", "tutorial_2")],
    )


async def tutorial_callback_query(
    query: types.CallbackQuery,
    message: str,
    media: str,
    keyboards: typing.Sequence[typing.Tuple[str, str]],
):
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
