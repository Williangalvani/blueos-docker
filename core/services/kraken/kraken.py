from typing import Any

import aiodocker
import aiohttp
import asyncio
import re

from commonwealth.settings.manager import Manager

from settings import Extension, SettingsV1

REPO_URL = "https://raw.githubusercontent.com/Williangalvani/BlueOS-Extensions-Repository/master/manifest.json"


class Kraken:
    def __init__(self):
        self.load_settings()
        self.containers = []
        self.running_containers = []
        self.should_run = True


    async def run(self):
        self.client = aiodocker.Docker()
        while self.should_run:
            await asyncio.sleep(5)
            self.running_containers = await self.client.containers.list(filter='{"status": ["running"]}')
            for extension in self.settings.extensions:
                await self.check(extension)
        

    async def start_extension(self, extension: Extension):
        config = extension.settings() 
        config['Image'] = extension.fullname()
        await self.client.images.pull(extension.fullname())
        container = await self.client.containers.create_or_replace(
            name=extension.container_name(),
            config=config
        )
        await container.start()

    async def check(self, extension: Extension):
        if not any(container["Names"][0][1:] == extension.container_name() for container in self.running_containers):
            await self.start_extension(extension)

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

    async def kill(self, container_name: str):
        print(f"killing {container_name}")
        container = await self.client.containers.list(filter=f"name={container_name}")
        if container:
            await container[0].kill()

    async def uninstall_extension(self, extension_name: str):
        regex = re.compile('[^a-zA-Z]')
        expected_container_name = "extension-" + regex.sub('', f"{extension_name}")
        extension = [extension for extension in self.settings.extensions if extension.name != expected_container_name]
        print(extension)
        if extension:
            await self.kill(extension[0].container_name())
        self.settings.extensions = [
            extension for extension in self.settings.extensions if extension.name != extension_name
        ]
        self.manager.save()

    async def list_containers(self):
        self.client = aiodocker.Docker()
        containers = await self.client.containers.list(filter='{"status": ["running"]}')
        print(containers)
        return containers

    async def stop(self):
        self.should_run = False
