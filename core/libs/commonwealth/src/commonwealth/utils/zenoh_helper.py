import asyncio
from typing import Any, Callable
import json
import concurrent.futures
import fastapi
import zenoh
from loguru import logger


class ZenohSession:
    session: zenoh.Session
    _executor = None

    def __init__(self, configuration: dict[str, Any]):
        config = zenoh.Config()
        for key, value in configuration.items():
            config.insert_json5(key, json.dumps(value))

        ZenohSession.session = zenoh.open(config)
        ZenohSession._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="zenoh-",
        )

    def close(self):
        self.session.close()
        self._executor.shutdown()

    @classmethod
    def zenoh_queryable(cls):
        def decorator(func: Callable[[], Any]):
            route_path = getattr(func, "_route_path", None)
            if route_path and route_path[0] == "/":
                route_path = route_path[1:]

            def wrapper(query: zenoh.Query):
                async def _handle_async():
                    try:
                        response = await func()
                        if response is not None:
                            query.reply(query.selector.key_expr, json.dumps(response, default=str))
                    except Exception as e:
                        error_response = {"error": str(e)}
                        query.reply(query.selector.key_expr, json.dumps(error_response))

                if ZenohSession._executor:
                    ZenohSession._executor.submit(asyncio.run, _handle_async())

            if route_path and ZenohSession.session:
                try:
                    ZenohSession.session.declare_queryable(route_path, wrapper)
                except Exception as e:
                    logger.error(f"Error declaring queryable {route_path}: {e}")

        return decorator


def route_info_decorator(deco):
    def wrapper(path, *args, **kwargs):
        def inner(func):
            func._route_path = path
            return deco(path, *args, **kwargs)(func)

        return inner

    return wrapper


def apply_route_decorator(app: fastapi.FastAPI):
    app.get = route_info_decorator(app.get)
    app.post = route_info_decorator(app.post)
    app.put = route_info_decorator(app.put)
    app.delete = route_info_decorator(app.delete)
    app.patch = route_info_decorator(app.patch)
    return app
