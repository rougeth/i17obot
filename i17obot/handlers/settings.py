import typing

from aiogram import types

from i17obot import bot, config, dp
from i17obot.database import get_user, toggle_reminder, update_user
from i17obot.models import User
from i17obot.templates import render_template
from i17obot.utils import check_user_state

from .translate import translate


@dp.message_handler(commands=["reminder", "lembrete", "recordatorio"])
async def reminder(message: types.Message):
    if not types.ChatType.is_private(message.chat):
        return

    reminder_set = await toggle_reminder(message.from_user.id)

    template_name = "reminder_on" if reminder_set else "reminder_off"
    response = await render_template(message.from_user.id, template_name)

    await bot.send_message(
        message.chat.id, response, parse_mode="markdown",
    )


@dp.message_handler(commands=["language"])
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


@dp.callback_query_handler(lambda query: query.data in config.AVAILABLE_LANGUAGES)
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


@dp.message_handler(commands=["projects", "project"])
async def projects(message: types.Message):
    await types.ChatActions.typing()
    user = await get_user(message.from_user.id)
    user_project = user.get("project", "")

    if user_project:
        template = await render_template(
            user["id"], "list_projects", project=user_project
        )
    else:
        template = await render_template(user["id"], "list_projects_start")

    keyboard_markup = types.InlineKeyboardMarkup()
    for code, project in config.AVAILABLE_PROJECTS.items():
        if code != user_project:
            keyboard_markup.row(types.InlineKeyboardButton(project, callback_data=code))

    await bot.send_message(
        message.chat.id,
        template,
        disable_web_page_preview=True,
        parse_mode="markdown",
        reply_markup=keyboard_markup,
    )


@dp.callback_query_handler(lambda query: query.data in config.AVAILABLE_PROJECTS)
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


@dp.callback_query_handler(text="configure-username")
async def transifex_username(query: types.CallbackQuery):
    user = await User.get(query.from_user.id)
    user.configure_transifex()
    await user.update()

    template = await render_template(query.from_user.id, "configuring_username")

    await bot.edit_message_text(
        template,
        query.message.chat.id,
        query.message.message_id,
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )


@dp.callback_query_handler(check_user_state("configuring_transifex"), run_task=True)
async def set_transifex_username(message: types.Message):
    user = await User.get(message.from_user.id)
    username = message.text.strip()
    user.transifex_username = username
    user.transifex_configured()
    await user.update()

    if user.translating_string:
        await bot.send_message(
            user.id,
            f"👍 *Usuário `{username}` configurado com sucesso!*\nContinue com a tradução...",
            parse_mode="Markdown",
        )
        string = user.translating_string
        await translate(message, string["resource"], string)
    else:
        await bot.send_message(
            user.id,
            f"👍 *Usuário `{username}` configurado com sucesso!*",
            parse_mode="Markdown",
        )
