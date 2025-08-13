#! /usr/bin/env python3
import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict

import appdirs
import dpath
from commonwealth.utils.logs import InterceptHandler, init_logger
from commonwealth.utils.sentry_config import init_sentry_async
from loguru import logger
from robyn import Robyn, Request, Response
from robyn.responses import serve_html

SERVICE_NAME = "bag-of-holding"
FILE_PATH = Path(appdirs.user_config_dir(SERVICE_NAME, "db.json"))

logging.basicConfig(handlers=[InterceptHandler()], level=0)
init_logger(SERVICE_NAME)

app = Robyn(__file__)
logger.info(f"Starting Bag of Holding: {FILE_PATH}")


def read_db() -> Any:
    try:
        with open(FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("Database not found")
    except json.decoder.JSONDecodeError as exception:
        logger.error(f"Failed to parse json in database file: {exception}")
    except Exception as exception:
        logger.exception(exception)
    return {}


def write_db(data: Dict[str, Any]) -> None:
    # Just to be sure that we'll be able to load it later
    json_string = json.dumps(data)
    json.loads(json_string)

    with open(FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


@app.post("/overwrite")
async def overwrite_data(request: Request) -> Response:
    payload = request.json()
    logger.debug(f"Overwrite: {json.dumps(payload)}")
    write_db(payload)
    return Response(status_code=200, headers={}, description=json.dumps({"status": "success"}))


async def write_data_handler(request: Request) -> Response:
    path = request.path_params.get("path")
    payload = request.json()
    logger.debug(f"Write path: {path}, {json.dumps(payload)}")
    current_data = read_db()
    dpath.new(current_data, path, payload)
    write_db(current_data)
    return Response(status_code=200, headers={}, description=json.dumps({"status": "success"}))


async def read_data_handler(request: Request) -> Response:
    path = request.path_params.get("path")
    logger.debug(f"Get path: {path}")
    current_data = read_db()

    if path == "*":
        return Response(status_code=200, headers={}, description=json.dumps(current_data))

    try:
        result = dpath.get(current_data, path)
        return Response(status_code=200, headers={}, description=json.dumps(result))
    except KeyError:
        return Response(status_code=400, headers={}, description=json.dumps({"detail": "Invalid path"}))


# Register versioned routes
@app.post("/v1.0/set/:path")
async def write_data_v1(request: Request) -> Response:
    return await write_data_handler(request)


@app.get("/v1.0/get/:path")
async def read_data_v1(request: Request) -> Response:
    return await read_data_handler(request)


# Register latest routes (equivalent to versioned)
@app.post("/latest/set/:path")
async def write_data_latest(request: Request) -> Response:
    return await write_data_handler(request)


@app.get("/latest/get/:path")
async def read_data_latest(request: Request) -> Response:
    return await read_data_handler(request)


@app.get("/")
async def root(request: Request) -> Response:
    html_content = """
    <html>
        <head>
            <title>Bag Of Holding</title>
        </head>
    </html>
    """
    return serve_html(html_content)


async def main() -> None:
    await init_sentry_async(SERVICE_NAME)
    
    # Start the Robyn server
    app.start(host="0.0.0.0", port=9101)


if __name__ == "__main__":
    asyncio.run(main())
