import logging
import typing

from aiogram import types
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiogram.utils.markdown import quote_html

from i17obot import bot, config, dp
from i17obot.database import get_user, save_translated_string, update_user
from i17obot.models import User
from i17obot.templates import render_template
from i17obot.transifex import (
    random_string,
    review_string,
    transifex_string_url,
    translate_string,
)
from i17obot.utils import check_user_state, docsurl, make_keyboard, unparse_message

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


@dp.message_handler(commands=["translate", "traduzir", "traducir"])
@dp.callback_query_handler(text="translate")
async def translate(
    message: typing.Union[types.CallbackQuery, types.Message], string=None
):
    user_id = message.from_user.id
    if isinstance(message, types.Message):
        message_id = message.message_id
        chat_id = message.chat.id
    else:
        message_id = message.message.message_id
        chat_id = message.message.chat.id

    await bot.send_chat_action(chat_id, "typing")
    user = await User.get(user_id)
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

    if user.is_beta:
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
                message_1, chat_id, message_id - 1, parse_mode="markdown",
            )
            await bot.edit_message_text(
                message_2, chat_id, message_id, **options,
            )

    except BotBlocked:
        logger.exception("i17obot blocked by user. userid=%r", user.id)
    except TelegramAPIError:
        logger.exception(
            "Telegram API Error while sending message. message_1=%r, message_2=%r",
            message_1,
            message_2,
        )


@dp.callback_query_handler(text="init-translation")
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


@dp.message_handler(check_user_state("translating"), run_task=True)
async def review(message: types.Message):
    translation = unparse_message(message) if message.entities else message.text

    user = await User.get(message.from_user.id)
    user.confirm_translation()
    user.translating_string.translation = translation
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
        translation=translation,
    )

    await bot.send_message(
        user.id,
        response,
        disable_web_page_preview=True,
        reply_markup=keyboard_markup,
        parse_mode="Markdown",
    )


@dp.callback_query_handler(text="confirm-translation")
async def confirm_translation(query: types.CallbackQuery):
    user = await User.get(query.from_user.id)
    response = await render_template(
        user.id,
        "confirm_translation",
        source=user.translating_string.source,
        translation=user.translating_string.translation,
    ) + (
        "\n🎉 *Tradução confirmada com sucesso!*"
        "\nQue tal /traduzir mais um trecho? 😁"
    )

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


@dp.callback_query_handler(
    lambda query: query.data
    in ["confirm-translation", "translate-again", "cancel-translating"]
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
