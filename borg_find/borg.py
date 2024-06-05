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
                flag="c",  # read/write/create if necessary
            )

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
        return zlib.compress(obj)

    def my_decode(self, obj):
        return zlib.decompress(obj)

    def _read_cache(self, uid: Optional[str]) -> Optional[bytes]:
        try:
            cached = self.db[uid]
        except KeyError:
            cached = None

        return cached

    def _write_cache(self, uid: Optional[str], data: bytes):

        if data:
            self.db[uid] = data
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
