#!/usr/bin/env python

import errno
import os
import time
from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser
from typing import Any, Dict, Optional

from fuse import FUSE, FuseOSError, LoggingMixIn, Operations
from loguru import logger
from pymavlink import mavutil

from mavftp import FTPModule

base_file_paths = ["/", "@ROMFS", "@SYS"]


class MAVFTP(LoggingMixIn, Operations):
    def __init__(self, mav: Any) -> None:
        self.mav = mav
        self.files: Dict[str, Dict[str, int]] = {
            path: {
                "st_mode": 0o40755,
                "st_nlink": 2,
                "st_size": 0,
                "st_ctime": int(time.time()),
                "st_mtime": int(time.time()),
                "st_atime": int(time.time()),
            }
            for path in base_file_paths
        }
        self.ftp = FTPModule(mav)

    def fix_path(self, path: str) -> str:
        if path.startswith("/@"):
            return path[1:]
        return path

    def getattr(self, path: str, _fh: int = 0) -> Any:
        path_fixed = self.fix_path(path)
        logger.info(f"Fuse: getattr {path_fixed}")
        if path_fixed in self.files:
            return self.files[path_fixed]

        parent_dir = ("/" + "/".join(path.split("/")[:-1])).replace("//", "/")
        logger.debug(f"cache miss, asking for {parent_dir}")
        self.readdir(parent_dir)
        if path not in self.files:
            raise FuseOSError(errno.ENOENT)
        return self.files[path]

    def read(self, path: str, size: int, offset: int, _fh: int = 0) -> Optional[bytes]:
        buf = self.ftp.read_sector(self.fix_path(path), offset, size)
        # logger.info(f"read result: {buf}")
        return buf

    def readdir(self, path: str, _fh: int = 0) -> Any:
        path_fixed = self.fix_path(path)
        logger.info(f"Fuse: readdir {path_fixed}")
        directory = self.ftp.list(path_fixed)
        if directory is None or len(directory) == 0:
            return []
        ret = {}
        for item in directory:
            if item.name in [".", ".."]:
                continue
            if not item.is_dir:
                new_item = {"st_mode": (0o100444), "st_size": item.size_b}
            else:
                new_item = {
                    "st_mode": (0o46766),
                    "st_nlink": 2,  # Self-link and parent link
                    "st_size": 0,  # Size 0 for simplicity
                    "st_ctime": int(time.time()),  # Current time
                    "st_mtime": int(time.time()),  # Current time
                    "st_atime": int(time.time()),  # Current time
                }
            ret[item.name] = new_item
            new_path = path if path.endswith("/") else path + "/"
            self.files[new_path + item.name] = new_item
        self.files[path] = {"st_mode": (0o46766), "st_size": 0}
        return ret

    def ensure_file_exists(self, path: str) -> None:
        logger.info(f"making sure {path} exists...")
        try:
            self.get_path(path)
        except FuseOSError as e:
            logger.info(f"{path} didn't exist({e}). creating it...")
            self.create(path)

    def create(self, path: str, fi: int = 0) -> None:
        """
        When raw_fi is False (default case), fi is None and create should
        return a numerical file handle.

        When raw_fi is True the file handle should be set directly by create
        and return 0.
        """
        logger.info(f"Fuse: create {path}, fi={fi}")
        raise FuseOSError(errno.ENOENT)

    def mknod(self, path: str) -> None:
        logger.error(f"Fuse: lookup {path}")
        raise FuseOSError(errno.ENOENT)

    def write(self, path: str, _data: bytes, _offset: int, _fh: int) -> None:
        logger.error(f"Fuse: write {path}")
        raise FuseOSError(errno.EROFS)

    def mkdir(self, path: str, _mode: int) -> None:
        logger.error(f"Fuse: mkdir {path}")
        raise FuseOSError(errno.EROFS)

    def rmdir(self, path: str) -> None:
        logger.error(f"Fuse: rmdir {path}")
        raise FuseOSError(errno.EROFS)

    def unlink(self, path: str) -> None:
        logger.error(f"Fuse: unlink {path}")
        raise FuseOSError(errno.EROFS)

    def rename(self, old: str, new: str) -> None:
        logger.error(f"Fuse: rename {old} -> {new}")
        raise FuseOSError(errno.EROFS)

    def chmod(self, path: str, _mode: int) -> None:
        logger.error(f"Fuse: chmod {path}")
        raise FuseOSError(errno.EROFS)

    def chown(self, path: str, _uid: int, _gid: int) -> None:
        logger.error(f"Fuse: chown {path}")
        raise FuseOSError(errno.EROFS)

    def truncate(self, path: str) -> None:
        logger.info(f"Fuse: truncate {path}")
        raise FuseOSError(errno.EROFS)


if __name__ == "__main__":
    # logging.basicConfig(level=logging.DEBUG)
    parser = ArgumentParser(description="MAVLink FTP", formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-m",
        "--mavlink",
        default="udpin:127.0.0.1:14555",
        help="MAVLink connection specifier",
    )
    parser.add_argument(
        "--mountpoint",
        help="Path to the mountpoint",
    )

    args = parser.parse_args()

    if not os.path.exists(args.mountpoint):
        os.makedirs(args.mountpoint)

    fuse = FUSE(
        MAVFTP(mavutil.mavlink_connection(args.mavlink)),
        args.mountpoint,
        foreground=True,
        ro=True,
        nothreads=True,
        allow_other=True,
    )
