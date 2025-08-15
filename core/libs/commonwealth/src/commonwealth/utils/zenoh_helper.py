import asyncio
import atexit
import os
import sys
import time
import threading
import signal
from typing import Any, Callable, Set
import json
import concurrent.futures
import fastapi
import zenoh
from loguru import logger


class ZenohSession:
    session: zenoh.Session
    _executor = None
    _queryables: Set[zenoh.Queryable] = set()
    _shutdown_event = threading.Event()
    _shutdown_registered = False

    def __init__(self, configuration: dict[str, Any]):
        config = zenoh.Config()
        for key, value in configuration.items():
            config.insert_json5(key, json.dumps(value))

        ZenohSession.session = zenoh.open(config)
        ZenohSession._executor = concurrent.futures.ThreadPoolExecutor(
            max_workers=4,
            thread_name_prefix="zenoh-",
        )

        if not ZenohSession._shutdown_registered:
            ZenohSession._register_shutdown_handlers()
            ZenohSession._shutdown_registered = True

    @classmethod
    def _register_shutdown_handlers(cls):
        atexit.register(ZenohSession._shutdown)

        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, {frame}, shutting down")
            ZenohSession._shutdown()

            def force_exit():
                time.sleep(1)
                logger.warning("Force killing process")
                os._exit(1)

            threading.Thread(target=force_exit, daemon=True).start()
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        if hasattr(signal, "SIGHUP"):
            signal.signal(signal.SIGHUP, signal_handler)

    @classmethod
    def _cleanup_executor(cls):
        if ZenohSession._executor:
            try:
                ZenohSession._executor.shutdown(wait=True)
                ZenohSession._executor = None
            except Exception as e:
                logger.error(f"Error shutting down Zenoh executor: {e}")

    @classmethod
    def _cleanup_session(cls):
        if ZenohSession.session:
            try:
                ZenohSession.session.close()
                ZenohSession.session = None
            except Exception as e:
                logger.error(f"Error closing Zenoh session: {e}")

    @classmethod
    def _cleanup_queryables(cls):
        for queryable in list(ZenohSession._queryables):
            try:
                queryable.undeclare()
            except Exception as e:
                logger.error(f"Error undeclaring queryable {queryable}: {e}")
            finally:
                ZenohSession._queryables.remove(queryable)
        ZenohSession._queryables.clear()

    @classmethod
    def _cleanup_remaining_threads(cls):
        try:
            remaining_threads = [
                t for t in threading.enumerate() if t != threading.current_thread() and t.name != "MainThread"
            ]

            if remaining_threads:
                logger.warning(f"Remaining threads: {[f'{t.name}(daemon={t.daemon})' for t in remaining_threads]}")

                for thread in remaining_threads:
                    if not thread.daemon and thread.is_alive():
                        try:
                            logger.debug(f"Joining thread: {thread.name}")
                            thread.join(timeout=2.0)
                        except Exception as e:
                            logger.error(f"Error joining thread {thread.name}: {e}")
            else:
                logger.info("All threads cleaned up successfully")

        except Exception as e:
            logger.error(f"Error in final thread cleanup: {e}")

    @classmethod
    def _shutdown(cls):
        logger.info("Shutting down Zenoh session")
        ZenohSession._shutdown_event.set()

        ZenohSession._cleanup_queryables()
        ZenohSession._cleanup_session()
        ZenohSession._cleanup_executor()
        ZenohSession._cleanup_remaining_threads()

    @classmethod
    def zenoh_queryable(cls):
        def decorator(func: Callable[[], Any]):
            route_path = getattr(func, "_route_path", None)
            if route_path and route_path[0] == "/":
                route_path = route_path[1:]

            def wrapper(query: zenoh.Query):
                if ZenohSession._shutdown_event.is_set():
                    logger.debug("Ignoring queryable request during shutdown")
                    return

                async def _handle_async():
                    try:
                        if ZenohSession._shutdown_event.is_set():
                            return

                        response = await func()
                        if response is not None and not ZenohSession._shutdown_event.is_set():
                            query.reply(query.selector.key_expr, json.dumps(response, default=str))
                    except Exception as e:
                        if not ZenohSession._shutdown_event.is_set():
                            error_response = {"error": str(e)}
                            query.reply(query.selector.key_expr, json.dumps(error_response))

                if ZenohSession._executor and not ZenohSession._shutdown_event.is_set():
                    ZenohSession._executor.submit(asyncio.run, _handle_async())

            if route_path and ZenohSession.session:
                try:
                    queryable = ZenohSession.session.declare_queryable(route_path, wrapper)
                    ZenohSession._queryables.add(queryable)
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
