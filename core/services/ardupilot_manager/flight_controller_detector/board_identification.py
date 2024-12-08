import json
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
import time

from pydantic import BaseModel

from flight_controller_detector.metadata_preprocessor import ManifestHandler
from typedefs import Platform
from loguru import logger


class SerialAttr(str, Enum):
    product = "product"
    manufacturer = "manufacturer"


class SerialBoardIdentifier(BaseModel):
    attribute: SerialAttr
    id_value: str
    platform: Platform


def get_boards_cache_path() -> Path:
    cache_dir = Path.home() / ".cache" / "boards"
    cache_dir.mkdir(parents=True, exist_ok=True)
    return cache_dir / "boards.json"


def load_board_identifiers() -> Dict[str, Dict[str, int]]:
    """Load board identifiers from the manifest, using cache when possible."""
    boards_path = get_boards_cache_path()

    handler = ManifestHandler()
    handler.process_and_export(boards_path)

    with open(boards_path, encoding="utf-8") as f:
        json_data = json.load(f)

    assert isinstance(json_data, dict), "json_data is not a dict"
    return json_data


def get_board_ids_from_usb_id(vid: int, pid: int, board_name: Optional[str] = None) -> List[int]:
    """
    Get the board ID for a given USB VID:PID combination, optionally filtering by board name, for
    cases where multiple boards share the same USB ID.
    """
    try:
        boards_path = get_boards_cache_path()

        if not boards_path.exists():
            handler = ManifestHandler()
            handler.process_and_export(boards_path)

        with open(boards_path, encoding="utf-8") as f:
            json_data = json.load(f)

        usb_id = f"{vid:04x}:{pid:04x}"
        if usb_id in json_data:
            boards_dict = json_data[usb_id]
            if board_name is not None and board_name in boards_dict:
                return [boards_dict[board_name]]
            logger.warning(f"No board_id found matching name {board_name}. returning unfiltered results.")
            return list(set(boards_dict.values()))

        return []
    except (json.JSONDecodeError, OSError, FileNotFoundError) as e:
        logger.warning(f"Error loading board identifiers: {e}")
        return []


def is_cache_valid() -> bool:
    """Check if the boards cache is valid and up to date."""
    boards_path = get_boards_cache_path()
    if not boards_path.exists():
        return False

    # Check if cache is older than 24 hours
    cache_age = time.time() - boards_path.stat().st_mtime
    return cache_age < 86400  # 24 hours in seconds
