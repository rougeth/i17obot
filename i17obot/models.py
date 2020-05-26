from dataclasses import asdict, dataclass
from datetime import datetime
from urllib.parse import quote

from transitions import Machine

from i17obot.database import db

PROJECT_URL = {
    "python": (
        "https://www.transifex.com/"
        "python-doc/python-newest/translate/#{language}/{resource}/1"
        "?q={query_string}"
    ),
    "jupyter": (
        "https://www.transifex.com/"
        "project-jupyter/jupyter-meta-documentation/translate/#{language}/{resource}/1"
        "?q={query_string}"
    ),
}


@dataclass
class String:
    project: str
    resource: str
    language: str
    source: str
    hash: str
    translation: str
    reviewed: bool

    @property
    def url(self):
        return PROJECT_URL[self.project].format(
            resource=self.resource,
            language=self.language,
            query_string=quote(f"text:'{self.source[:20]}'"),
        )

    def asdict(self):
        return asdict(self)

    @classmethod
    def from_transifex(cls, **kwargs):
        transifex_to_string_map = {
            "source": "source_string",
            "hash": "string_hash",
        }
        for valid_key, actual_key in transifex_to_string_map.items():
            if value := kwargs.get(actual_key):
                kwargs[valid_key] = kwargs.pop(actual_key)

        valid_keys = cls.__annotations__.keys()
        kwargs = {key: value for key, value in kwargs.items() if key in valid_keys}
        return cls(**kwargs)


@dataclass
class User:
    id: int
    reminder_set: bool
    telegram_data: dict
    chat_type: str
    updated_at: datetime = None
    transifex_username: str = None
    state: str = "idle"
    language_code: str = "pt_BR"
    project: str = "python"
    reviewing_string: String = None
    translating_string: String = None
    is_beta: bool = False

    _states = ["idle", "translating", "confirming_translation", "configuring_transifex"]
    _transitions = [
        {
            "trigger": "translate",
            "source": ["idle", "confirming_translation"],
            "dest": "translating",
        },
        {
            "trigger": "confirm_translation",
            "source": "translating",
            "dest": "confirming_translation",
        },
        {
            "trigger": "translation_confirmed",
            "source": "confirming_translation",
            "dest": "idle",
        },
        {"trigger": "cancel_translation", "source": "*", "dest": "idle"},
        {
            "trigger": "configure_transifex",
            "source": "idle",
            "dest": "configuring_transifex",
        },
        {
            "trigger": "transifex_configured",
            "source": "configuring_transifex",
            "dest": "idle",
        },
    ]

    def __post_init__(self):
        self.machine = Machine(
            self, states=self._states, transitions=self._transitions, initial=self.state
        )
        if isinstance(self.translating_string, dict):
            self.translating_string = String(**self.translating_string)

        if isinstance(self.reviewing_string, dict):
            self.reviewing_string = String(**self.reviewing_string)

    @classmethod
    async def get(cls, user_id):
        if not (data := await db.users.find_one({"id": user_id})):
            raise Exception("User not found")

        del data["_id"]
        return cls(**data)

    async def update(self):
        data = asdict(self)
        del data["id"]
        await db.users.update_one({"id": self.id}, {"$set": data})
