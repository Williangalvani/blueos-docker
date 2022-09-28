import aiohttp
import aiodocker
from settings import SettingsV1
from settings import Extension as SettingsExtension
from typing import Any
from pydantic import BaseModel
from commonwealth.settings.manager import Manager


class Extension(BaseModel):
    name: str
    tag: str
    additional_pemissions: Any
    enabled: bool

    @staticmethod
    def from_settings_spec(spec: SettingsExtension)  -> "Extension":
        return Extension(
            name=spec.name,
            tag=spec.tag,
            additional_pemissions=spec.additional_pemissions,
            enabled=spec.enabled
        )


class Kraken:

    def __init__(self):
        self.load_settings()
        print(self.settings)


    def load_settings(self):
        self.manager = Manager("Kraken", SettingsV1)
        self.settings = self.manager.settings


    async def fetch_manifest(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(REPO_URL) as resp:
                if resp.status != 200:
                    print(f"Error status {resp.status}")
                    raise Exception("Could not get auth token")
                return await resp.json(content_type=None)

    async def get_dockers(self):
        self.client = aiodocker.Docker()
        images = []
        for container in await self.client.containers.list():
            images.append(await container.stats(stream=False))
        return images


    async def get_configured_extensions(self):
        return self.settings.extensions


    async def install_extension(self, extension: SettingsExtension):
        self.settings.extensions.append(Extension.from_settings_spec(extension))