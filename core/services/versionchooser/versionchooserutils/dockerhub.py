#!/usr/bin/env python3
"""
Responsible for interacting with dockerhub
adapted from https://github.com/al4/docker-registry-list
"""

from typing import Dict, List, Optional
from warnings import warn

import aiohttp


# pylint: disable=too-few-public-methods
class TagFetcher:
    """Fetches remote tags for a given image"""

    # Holds the information once it is fetched so we don't do it multiple times
    cache: Dict[str, List[str]] = {}

    @staticmethod
    async def _get_token(auth_url: str, image_name: str) -> str:
        """[summary]
        Gets a token for dockerhub.com
        Args:
            auth_url: authentication url, default to https://auth.docker.io
            image_name: image name, for example "bluerobotics/core"

        Raises:
            Exception: Raised if unable to get the token

        Returns:
            The token
        """
        payload = {
            "service": "registry.docker.io",
            "scope": "repository:{image}:pull".format(image=image_name),
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(auth_url + "/token", params=payload) as resp:
                if resp.status != 200:
                    warn("Error status {}".format(resp.status))
                    raise Exception("Could not get auth token")
                return str((await resp.json())["token"])

    async def fetch_remote_tags(
        self,
        image_name: str,
        index_url: str = "https://index.docker.io",
        token: Optional[str] = None,
    ) -> List[str]:
        """Fetches the tags available for an image in DockerHub

        Args:
            image_name (str): Image to fetch tags for, for example "bluerobotics/core"
            index_url (str, optional): [description]. Defaults to "https://index.docker.io".
            token (Optional[str], optional): Token to use. Gets a new one if None is supplied

        Returns:
            List[str]: A list of tags available on DockerHub
        """
        if image_name in self.cache:
            return self.cache[image_name]

        header = None
        try:
            if token is None:
                token = await self._get_token(auth_url="https://auth.docker.io", image_name=image_name)
            header = {"Authorization": "Bearer {}".format(token)}
        except Exception as error:
            print(type(error), error)
            return []

        # request = requests.get("{}/v2/{}/tags/list".format(index_url, image_name), headers=header).json()
        async with aiohttp.ClientSession() as session:
            async with session.get("{}/v2/{}/tags/list".format(index_url, image_name), headers=header) as resp:
                if resp.status != 200:
                    warn("Error status {}".format(resp.status))
                    raise Exception("Failed getting tags from DockerHub!")
                data = await resp.json()

                if "tags" not in data:
                    return []
                tags = list(data["tags"])
                self.cache[image_name] = tags
                return tags
