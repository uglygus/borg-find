"""
borg wrapper
"""

import getpass
import os
import subprocess
import zlib
from dataclasses import dataclass
from json import loads
from pathlib import Path
from typing import List, Optional

from sqlitedict import SqliteDict


@dataclass
class Borg:
    binary: str
    cache_folder: Optional[Path] = None
    lock_wait: int = 10

    def __post_init__(self):
        os.environ["BORG_PASSPHRASE"] = getpass.getpass("Repository password: ")
        if self.cache_folder:
            self.cache_folder.mkdir(exist_ok=True, parents=True)
            self.db = SqliteDict(
                self.cache_folder / "borg-find.sqlite",
                outer_stack=False,
                tablename="archive",
                encode=self.my_encode,
                decode=self.my_decode,
                autocommit=True,
                flag="c",  # read/write create if necessary
            )
        else:
            print("ERROR no cache_folder")

    @property
    def _env(self):
        # Avoid interactive question when accessing repository
        out = dict(os.environ)
        out["BORG_RELOCATED_REPO_ACCESS_IS_OK"] = "yes"
        return out

    @property
    def _command(self) -> List[str]:
        return [self.binary, "--lock-wait", str(self.lock_wait)]

    def my_encode(self, obj):
        # print("encode: ", obj)

        return zlib.compress(obj)

    def my_decode(self, obj):
        # print("dencode: ", obj)
        return zlib.decompress(obj)

    # uid=ca4991bb8ecd419e887cc1780752f5ded95da11db101e9e817764f06c1f0bec0
    def _read_cache(self, uid: Optional[str]) -> Optional[bytes]:
        # print(f"_read_cache(uid={uid}")
        # print("len(db)=", len(self.db))
        try:
            cached = self.db[uid]
        except KeyError:
            print("Not cached - recaclulating. uid=", uid)
            cached = None

        return cached

    def _write_cache(self, uid: Optional[str], data: bytes):

        # cached = self._cached_file(uid)
        # print("\nwrite cache() , \n\tuid=", uid, "\n\tdata = ", data)
        if data:
            # print("\npre_data ==", data, "==\n")
            # print("pre_data type(data) == ", type(data), "\n")
            # print("post_data data.my_encode ==", data.my_encode(), "==\n")
            # print("post_data type(data.my_encode()) == ", type(data.my_encode()), "\n")
            # # input("...ok..")
            self.db[uid] = data
            # self.db.commit()
            # print("\ncommit()")
            return True
        return False

    def repo_info(self, repo: str) -> dict:
        command = self._command + ["info", repo, "--json"]
        process = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            check=True,
            capture_output=True,
            env=self._env,
        )
        return loads(process.stdout)

    def repo_list(self, repo: str) -> dict:
        command = self._command + ["list", str(repo), "--json"]
        process = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            check=True,
            capture_output=True,
            env=self._env,
        )
        return loads(process.stdout)

    def archive_list(self, archive: str, uid: str = None) -> List[dict]:
        data = self._read_cache(uid)
        # print("---ARCHIVE_LIST()--")
        # print("type data=", type(data))
        # print("data=", data)
        # input("here mf....")
        if data is None:
            command = self._command + ["list", archive, "--json-lines"]
            process = subprocess.run(
                command,
                stdin=subprocess.DEVNULL,
                check=True,
                capture_output=True,
                env=self._env,
            )
            data = process.stdout

            self._write_cache(uid, data)
        return [loads(line) for line in data.decode().splitlines()]

    def extract_file(self, archive: str, path: str) -> bytes:
        command = self._command + ["extract", "--stdout", archive, path]
        process = subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            check=True,
            capture_output=True,
            env=self._env,
        )
        return process.stdout
