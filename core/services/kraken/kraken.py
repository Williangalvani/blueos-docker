import aiohttp
import aiodocker
from settings import SettingsV1
from settings import Extension
from typing import Any
from commonwealth.settings.manager import Manager


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

    async def get_docker_stats(self):
        self.client = aiodocker.Docker()
        if self.containers:
            return self.containers
        containers = []
        for container in await self.client.containers.list():
            container_data = (await container.stats(stream=False))[-1]
            container_data['name'] = container_data['name'].replace("/","")
            container_data["managed"] = any(container_data["name"] in extension.name for extension in self.settings.extensions)
            containers.append((container_data))
        self.containers = containers
        return containers


    async def get_configured_extensions(self):
        return self.settings.extensions


    async def install_extension(self, extension):
        new_extension = Extension(
            name=extension.name,
            tag=extension.tag,
            permissions=extension.permissions,
            enabled=extension.enabled
        )
        self.settings.extensions.append(new_extension)
        self.manager.save()


    async def list_containers(self):
        self.client = aiodocker.Docker()
        containers = await self.client.containers.list(filter='{"status": ["running"]}')
        print(containers)
        return containers