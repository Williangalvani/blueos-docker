import json
import re
import socket
from typing import Any, Dict, List

import psutil
from commonwealth.settings import settings
from loguru import logger
from pykson import (
    IntegerField,
    JsonObject,
    ListField,
    BooleanField,
    ObjectField,
    ObjectListField,
    StringField,
)


class Extension(JsonObject):
    name = StringField()
    tag = StringField()
    additional_pemissions: JsonObject()
    enabled: BooleanField()

    def __repr__(self) -> str:
        return str(self.name)

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
