import config
from aiogram import types
from database import get_user, save_translated_string, update_user
from telegram import bot
from templates import render_template
from utils import docsurl
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiogram.utils.markdown import quote_html
from utils import make_keyboard

from models import User

from transifex import (
    random_string,
    review_string,
    transifex_string_url,
    translate_string,
)


async def translate(message: types.Message, string=None):
    await types.ChatActions.typing()
    user = await User.get(message.from_user.id)
    if user.state != "idle":
        user.cancel_translation()
        await user.update()

    if not string:
        string = await random_string(
            user.language_code, user.project, translated=False, max_size=30,
        )

        user.translating_string = string
        await user.update()

    message_1 = f"```\n{string.source}\n```"
    message_2 = await render_template(
        user.id, "translate", docsurl=docsurl(string.resource).replace("__", "\_\_"),
    )
    message_2 = quote_html(message_2)

    if user.id in config.BETA_USERS:
        keyboard_markup = make_keyboard(
            ("Traduzir no Transifex", string.url),
            ("Traduzir no Telegram", "init-translation"),
            [("⏭ Próximo", "translate"), ("❌ Cancelar", "cancel-translating"),],
        )
    else:
        keyboard_markup = make_keyboard(
            ("Traduzir no Transifex", string.url),
            [("⏭ Próximo", "translate"), ("❌ Cancelar", "cancel-translating"),],
        )

    options = {
        "disable_web_page_preview": True,
        "parse_mode": "markdown",
        "reply_markup": keyboard_markup,
    }
    try:
        if isinstance(message, types.Message):
            await bot.send_message(user.id, message_1, parse_mode="markdown")
            await bot.send_message(user.id, message_2, **options)
        else:
            await bot.edit_message_text(
                message_1,
                message.message.chat.id,
                message.message.message_id - 1,
                parse_mode="markdown",
            )
            await bot.edit_message_text(
                message_2,
                message.message.chat.id,
                message.message.message_id,
                **options,
            )

    except BotBlocked:
        logger.exception("i17obot blocked by user. userid=%r", user.id)
    except TelegramAPIError:
        logger.exception(
            "Telegram API Error while sending message. message=%r", response
        )


async def ask_for_translation(query: types.CallbackQuery):
    user = await User.get(query.from_user.id)

    if not user.transifex_username:
        response = await render_template(user.id, "missing_username")
        keyboard_markup = make_keyboard(
            ("⚙️ Configurar usuário", "configure-username"),
        )
        await bot.edit_message_text(
            quote_html(response),
            query.message.chat.id,
            query.message.message_id,
            disable_web_page_preview=True,
            reply_markup=keyboard_markup,
            parse_mode="Markdown",
        )
        return

    string = user.translating_string

    user.translate()
    await user.update()

    response = await render_template(
        user.id,
        "init_translation",
        source=string.source,
        transifex_url=string.url,
        docsurl=docsurl(string.resource).replace("__", "\_\_"),
    )

    await bot.edit_message_text(
        response,
        query.message.chat.id,
        query.message.message_id,
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )


async def review(message: types.Message):
    user = await User.get(message.from_user.id)
    user.confirm_translation()
    user.translating_string.translation = message.text
    await user.update()

    keyboard_markup = make_keyboard(
        ("✅ Confirmar tradução", "confirm-translation"),
        ("🔁 Corrigir tradução", "translate-again"),
        ("❌ Cancelar", "cancel-translating"),
    )

    response = await render_template(
        user.id,
        "confirm_translation",
        source=user.translating_string.source,
        translation=message.text,
    )

    await bot.send_message(
        user.id,
        response,
        disable_web_page_preview=True,
        reply_markup=keyboard_markup,
        parse_mode="Markdown",
    )


async def confirm_translation(query: types.CallbackQuery):
    user = await User.get(query.from_user.id)
    response = await render_template(
        user.id,
        "confirm_translation",
        source=user.translating_string.source,
        translation=user.translating_string.translation,
    ) + ("\n🎉 *Tradução confirmada com sucesso!*")

    await translate_string(user, user.translating_string)
    await save_translated_string(user, user.translating_string)
    user.translation_confirmed()
    user.translating_string = None
    await user.update()

    await bot.edit_message_text(
        response,
        query.message.chat.id,
        query.message.message_id,
        disable_web_page_preview=True,
        parse_mode="Markdown",
    )


async def confirm(query: types.CallbackQuery):
    user = await User.get(query.from_user.id)

    if query.data == "translate-again":
        user.translate()
        await user.update()
        await bot.edit_message_text(
            "*Digite tradução abaixo:*",
            query.message.chat.id,
            query.message.message_id,
            parse_mode="Markdown",
        )
    elif query.data == "cancel-translating":
        user.cancel_translation()
        user.translating_string = None
        await user.update()
        await bot.edit_message_text(
            f"❌ *Tradução cancelada.* Sem problemas, {user.telegram_data['first_name']} 👍",
            query.message.chat.id,
            query.message.message_id,
            parse_mode="Markdown",
        )
