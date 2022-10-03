import asyncio
import re
from typing import Any, List, cast

import aiodocker
import aiohttp
from aiodocker.docker import DockerContainer
from commonwealth.settings.manager import Manager
from loguru import logger

from settings import Extension, SettingsV1

REPO_URL = "https://williangalvani.github.io/BlueOS-Extensions-Repository/manifest.json"


class Kraken:
    def __init__(self) -> None:
        self.load_settings()
        self.running_containers: List[DockerContainer] = []
        self.should_run = True

    async def run(self) -> None:
        self.client = aiodocker.Docker()
        while self.should_run:
            await asyncio.sleep(5)
            running_containers: List[DockerContainer] = await self.client.containers.list(  # type: ignore
                filter='{"status": ["running"]}'
            )
            self.running_containers = running_containers

            for extension in self.settings.extensions:
                await self.check(extension)

    async def start_extension(self, extension: Extension) -> None:
        config = extension.settings()
        config["Image"] = extension.fullname()
        logger.info(f"Starting extension '{extension.fullname()}'")
        await self.client.images.pull(extension.fullname())
        container = await self.client.containers.create_or_replace(name=extension.container_name(), config=config)  # type: ignore
        await container.start()

    async def check(self, extension: Extension) -> None:
        if not any(container["Names"][0][1:] == extension.container_name() for container in self.running_containers):
            await self.start_extension(extension)

    def load_settings(self) -> None:
        self.manager = Manager("Kraken", SettingsV1)
        self.settings = self.manager.settings

    async def fetch_manifest(self) -> Any:
        async with aiohttp.ClientSession() as session:
            async with session.get(REPO_URL) as resp:
                if resp.status != 200:
                    print(f"Error status {resp.status}")
                    raise Exception("Could not get auth token")
                return await resp.json(content_type=None)

    async def get_configured_extensions(self) -> List[Extension]:
        return cast(List[Extension], self.settings.extensions)

    async def install_extension(self, extension: Any) -> None:
        if any(extension.name == installed_extension.name for installed_extension in self.settings.extensions):
            # already installed
            return
        new_extension = Extension(
            name=extension.name, tag=extension.tag, permissions=extension.permissions, enabled=extension.enabled
        )
        self.settings.extensions.append(new_extension)
        self.manager.save()

    async def kill(self, container_name: str) -> None:
        logger.info(f"Killing {container_name}")
        container = await self.client.containers.list(filter=f"name={container_name}")  # type: ignore
        if container:
            await container[0].kill()

    async def uninstall_extension(self, extension_name: str) -> None:
        regex = re.compile("[^a-zA-Z0-9]")
        expected_container_name = "extension-" + regex.sub("", f"{extension_name}")
        extension = [
            extension
            for extension in self.settings.extensions
            if extension.container_name().startswith(expected_container_name)
        ]
        logger.info(f"uninstalling: {extension}")
        if extension:
            await self.kill(extension[0].container_name())
        self.settings.extensions = [
            extension for extension in self.settings.extensions if extension.name != extension_name
        ]
        self.manager.save()

    async def list_containers(self) -> List[DockerContainer]:
        self.client = aiodocker.Docker()
        containers: List[DockerContainer] = await self.client.containers.list(filter='{"status": ["running"]}')  # type: ignore
        return containers

    async def stop(self) -> None:
        self.should_run = False
