from typing import Any

import aiodocker
import aiohttp
from commonwealth.settings.manager import Manager

from settings import Extension, SettingsV1

REPO_URL = "https://raw.githubusercontent.com/Williangalvani/BlueOS-Extensions-Repository/master/manifest.json"


class Kraken:
    def __init__(self):
        self.load_settings()
        self.containers = []

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

    async def get_configured_extensions(self):
        return self.settings.extensions

    async def install_extension(self, extension):
        if any(extension.name == installed_extension.name for installed_extension in self.settings.extensions):
            # already installed
            return
        new_extension = Extension(
            name=extension.name, tag=extension.tag, permissions=extension.permissions, enabled=extension.enabled
        )
        self.settings.extensions.append(new_extension)
        self.manager.save()

    async def uninstall_extension(self, extension_name: str):
        self.settings.extensions = [
            extension for extension in self.settings.extensions
            if extension.name != extension_name
        ]
        self.manager.save()

    async def list_containers(self):
        self.client = aiodocker.Docker()
        containers = await self.client.containers.list(filter='{"status": ["running"]}')
        print(containers)
        return containers
