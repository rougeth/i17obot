from importlib import import_module

import config
from database import get_user


def get_template(language, template_name):
    try:
        mod = import_module(f"templates.{language.lower()}")
    except ModuleNotFoundError:
        mod = import_module(f"templates.{config.DEFAULT_LANGUAGE.lower()}")

    if not (template := getattr(mod, template_name)):
        raise Exception(f"Template not found for {language} language")

    return template


async def get_template_for_user(user_id, template_name):
    user = await get_user(user_id)
    language = user.get("language_code") or config.DEFAULT_LANGUAGE

    return get_template(language, template_name)
