import re
from typing import Any, Dict, List
import re
import json

from commonwealth.settings import settings
from loguru import logger
from pykson import (
    BooleanField,
    JsonObject,
    ObjectListField,
    StringField,
)


class Extension(JsonObject):
    name = StringField()
    tag = StringField()
    permissions = StringField()
    enabled = BooleanField()

    def settings(self):
        return json.loads(self.permissions)

    def fullname(self):
        return f"{self.name}:{self.tag}"

    def container_name(self):
        regex = re.compile('[^a-zA-Z]')
        return "extension-" + regex.sub('', f"{self.name}{self.tag}")


class SettingsV1(settings.BaseSettings):
    VERSION = 1
    extensions = ObjectListField(Extension)

    def __init__(self, *args: str, **kwargs: int) -> None:
        super().__init__(*args, **kwargs)

        self.VERSION = SettingsV1.VERSION

    def migrate(self, data: Dict[str, Any]) -> None:
        if data["VERSION"] == SettingsV1.VERSION:
            return

        if data["VERSION"] < SettingsV1.VERSION:
            super().migrate(data)

        data["VERSION"] = SettingsV1.VERSION
