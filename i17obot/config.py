import os

import decouple

BASE_DIR = os.path.dirname(__file__)

DATABASE = decouple.config("DATABASE")

ADMINS = decouple.config("ADMINS", default="", cast=decouple.Csv(int))
BETA_USERS = decouple.config("BETA_USERS", default="", cast=decouple.Csv(int))

DEFAULT_LANGUAGE = "pt_BR"
DEFAULT_PROJECT = "python"
AVAILABLE_LANGUAGES = {
    "pt_BR": "Brazilian Portuguese",
    "es": "Spanish",
}

AVAILABLE_PROJECTS = {
    "python": "Python",
    "jupyter": "Jupyter",
}

SENTRY_DSN = decouple.config("SENTRY_DSN", default="")
