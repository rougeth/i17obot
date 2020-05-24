import os
import typing

from aiogram import types

from i17obot import bot, config, dp
from i17obot.templates import render_template


@dp.message_handler(commands=["tutorial"])
@dp.callback_query_handler(text="tutorial_1")
async def part_1(message: types.Message):
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


@dp.callback_query_handler(text="tutorial_2")
async def part_2(query: types.CallbackQuery):
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


@dp.callback_query_handler(text="tutorial_3")
async def part_3(query: types.CallbackQuery):
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
