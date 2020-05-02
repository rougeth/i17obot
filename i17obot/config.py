import os

import decouple


BASE_DIR = os.path.dirname(__file__)

DATABASE = decouple.config("DATABASE")

ADMINS = decouple.config("ADMINS", cast=decouple.Csv(int))

AVAILABLE_LANGUAGES = {
    "pt_br": "Brazilian Portuguese",
    "es": "Spanish",
}
