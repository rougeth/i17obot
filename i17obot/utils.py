from collections import defaultdict
from datetime import datetime

from aiogram import types

from i17obot.models import User


def docsurl(resource):
    corner_cases = {
        "library--multiprocessing_shared_memory": "library/multiprocessing.shared_memory",
    }

    docspath = corner_cases.get(resource)
    if not docspath:
        docspath = "/".join(resource.split("--"))
        docspath = docspath.replace("_", ".").replace("..", "__")

    return f"https://docs.python.org/pt-br/3/{docspath}.html"


def check_user_state(state):
    async def wrapper(message: types.Message):
        user = await User.get(message.from_user.id)

        result = state == user.state
        print(user.state, state, result)
        return state == user.state

    return wrapper


def add_keyboard_button(label, data):
    key = "url" if data.startswith("http") else "callback_data"
    return types.InlineKeyboardButton(label, **{key: data})


def make_keyboard(*rows):
    keyboard_markup = types.InlineKeyboardMarkup()

    for row in rows:
        if isinstance(row, list):
            keyboard_markup.row(
                *[add_keyboard_button(button, data) for button, data in row]
            )
        else:
            keyboard_markup.row(add_keyboard_button(row[0], row[1]))

    return keyboard_markup


def sum_stats(stats):
    result = defaultdict(int)
    keys = [
        "translated_entities",
        "untranslated_entities",
        "translated_words",
        "untranslated_words",
        "reviewed",
    ]
    for data in stats:
        for key in keys:
            result[key] += data[key]

    total_entities = result["translated_entities"] + result["untranslated_entities"]
    result["total_translated"] = result["translated_entities"] / total_entities * 100
    result["total_reviewed"] = result["reviewed"] / total_entities * 100

    return result


def seconds_until_tomorrow(today):
    tomorrow = today + datetime.timedelta(days=1)
    return datetime.combine(tomorrow, datetime.time.min) - today
