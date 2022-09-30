#! /usr/bin/env python3
import logging
import shutil
import subprocess
import time
from enum import Enum
from pathlib import Path
from typing import Any
import aiohttp

import appdirs
import uvicorn
from commonwealth.utils.apis import GenericErrorHandlingRoute
from commonwealth.utils.decorators import temporary_cache
from commonwealth.utils.logs import InterceptHandler, get_new_log_path
from pydantic import BaseModel
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from fastapi_versioning import VersionedFastAPI, version
from loguru import logger
from kraken import Kraken

class Extension(BaseModel):
    name: str
    tag: str
    permissions: str
    enabled: bool


SERVICE_NAME = "kraken"

logging.basicConfig(handlers=[InterceptHandler()], level=0)

kraken = Kraken()

try:
    logger.add(get_new_log_path(SERVICE_NAME))
except Exception as e:
    print(f"unable to set logging path: {e}")


app = FastAPI(
    title="Kraken API",
    description="Kraken is the BlueOS service responsible for installing and managing thirdy-party extensions.",
)
app.router.route_class = GenericErrorHandlingRoute
logger.info("Releasing the Kraken!")


@app.get("/extensions_manifest", status_code=status.HTTP_200_OK)
# @temporary_cache(timeout_seconds=300)
@version(1, 0)
async def fetch_manifest() -> Any:
    return await kraken.fetch_manifest()

@app.get("/installed_extensions", status_code=status.HTTP_200_OK)
# @temporary_cache(timeout_seconds=300)
@version(1, 0)
async def get_installed_extensions() -> Any:
    return await kraken.get_configured_extensions()

@app.post("/install_extension", status_code=status.HTTP_201_CREATED)
@version(1, 0)
async def install_extension(extension: Extension) -> Any:
    return await kraken.install_extension(extension)

@app.get("/docker_stats", status_code=status.HTTP_200_OK)
@version(1, 0)
async def get_dockers_stats() -> Any:
    return await kraken.get_dockers_stats()

@app.get("/list_containers", status_code=status.HTTP_200_OK)
@version(1, 0)
async def list_containers() -> Any:
    containers =  await kraken.list_containers()
    return [{
        "name": container["Names"][0    ],
        "image": container["Image"],
        "imageId": container["ImageID"]

    } for container in containers]




app = VersionedFastAPI(app, version="1.0.0", prefix_format="/v{major}.{minor}", enable_latest=True)

@app.get("/")
async def root() -> Any:
    html_content = """
    <html>
        <head>
            <title>Kraken</title>
        </head>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)


if __name__ == "__main__":
    # Running uvicorn with log disabled so loguru can handle it
    uvicorn.run(app, host="0.0.0.0", port=9134, log_config=None)
