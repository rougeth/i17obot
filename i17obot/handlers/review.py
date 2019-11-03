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
from telegram import bot
from database import database


YES_NO = {"yes": "👍 Sim", "no": "👎 Não"}
YES_NO_DONOTKNOW = YES_NO.copy()
YES_NO_DONOTKNOW.update({"donotknow": "❔ Não sei"})


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
