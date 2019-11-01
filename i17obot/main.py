import asyncio
import logging
import os

import aiohttp
from aiogram import Bot, Dispatcher, types
from aiogram.types import inline_keyboard
from aiogram.utils import exceptions, executor
from decouple import config

import messages
from middlewares import UserDatabaseMiddleware
from transifex import transifex_api, random_string


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("broadcast")

YES_NO = {"yes": "👍 Sim", "no": "👎 Não"}
YES_NO_DONOTKNOW = YES_NO.copy()
YES_NO_DONOTKNOW.update({"donotknow": "❔ Não sei"})

database = {}
loop = asyncio.get_event_loop()
bot = Bot(token=config("TELEGRAM_TOKEN"), loop=loop, parse_mode=types.ParseMode.HTML)


def expected_state(state: str):
    def f(message: types.Message):
        user = database.get(message.from_user.id)
        if not user:
            raise Exception("User not found")

        valid_state = user.state == state
        if not valid_state:
            logger.error(
                "Unexpected state, user_state=%s, expected_state=%s", user.state, state
            )
        return valid_state

    return f


def yes_no_keyboard(question_button=False):
    buttons = YES_NO if not question_button else YES_NO_DONOTKNOW
    keyboard = inline_keyboard.InlineKeyboardMarkup()

    for id, text in buttons.items():
        keyboard.insert(inline_keyboard.InlineKeyboardButton(text, callback_data=id))

    return keyboard


async def review_start(message: types.Message):
    string = await random_string()

    await bot.send_message(
        message.chat.id,
        messages.review.format(
            original_text=string["source_string"], translation=string["translation"]
        ),
        parse_mode="Markdown",
    )
    await bot.send_message(
        message.chat.id,
        "A tradução está correta?",
        reply_markup=yes_no_keyboard(question_button=True),
        parse_mode="Markdown",
    )
    user = database.get(message.from_user.id)
    user.review()


async def review(callback_query: types.CallbackQuery):
    user = database.get(callback_query.from_user.id)

    edit_text = "{}\n*Resposta: {}*".format(
        callback_query.message.text, YES_NO_DONOTKNOW[callback_query.data]
    )
    await callback_query.message.edit_text(text=edit_text, parse_mode="Markdown")

    if callback_query.data == "yes":
        user_name = callback_query.from_user.first_name
        await bot.send_message(
            callback_query.message.chat.id,
            (
                f"Tradução revisada com *sucesso*, "
                f"obrigado pela contribuição, {user_name}! 🎉"
            ),
            parse_mode="Markdown",
        )
        user.reviewed()

    elif callback_query.data == "no":
        user_name = callback_query.from_user.first_name
        await bot.send_message(
            callback_query.message.chat.id,
            (
                f"Tradução revisada com *sucesso* e enviada para *correção*. "
                f"Obrigado pela contribuição, {user_name}! 🎉"
            ),
            parse_mode="Markdown",
        )
        user.reviewed()
    elif callback_query.data == "donotknow":
        user_name = callback_query.from_user.first_name
        await bot.send_message(
            callback_query.message.chat.id,
            (
                f"Sem problemas {user_name}, se você quiser revisar "
                f"outro texto, clique em /revisar."
            ),
        )
        user.reviewed()
    else:
        await callback_query.answer("Alguma coisa estranha aconteceu 👀")
        user.reviewed()


async def refine(callback_query: types.CallbackQuery):
    user = database.get(callback_query.from_user.id)

    edit_text = "{}\n*Resposta: {}*".format(
        callback_query.message.text, YES_NO[callback_query.data]
    )
    await callback_query.message.edit_text(text=edit_text, parse_mode="Markdown")

    if callback_query.data == "yes":
        await bot.send_message(
            callback_query.message.chat.id, "Envie tradução corrigida:"
        )
    elif callback_query.data == "no":
        await bot.send_message(
            callback_query.message.chat.id,
            "Tudo bem, adicionamos o texto na fila para correção. Muito obrigado!",
            reply_markup=None,
        )
        user.refined()
    else:
        await callback_query.answer("Alguma coisa estranha aconteceu 👀")
        user.reviewed()


async def refining(message: types.Message):
    await bot.send_message(message.chat.id, "Tradução corrigida:")
    await bot.send_message(
        message.chat.id, f"```\n{message.text}\n```", parse_mode="Markdown"
    )
    user = database.get(message.from_user.id)
    user.refined()


if __name__ == "__main__":
    dp = Dispatcher(bot, loop=loop)
    dp.middleware.setup(UserDatabaseMiddleware(database))

    dp.register_message_handler(review_start, expected_state("asleep"), commands=["review", "revisar"])
    dp.register_callback_query_handler(review, expected_state("reviewing"))
    dp.register_callback_query_handler(refine, expected_state("refining"))
    dp.register_message_handler(refining, expected_state("refining"))

    executor.start_polling(dp, skip_updates=True)
