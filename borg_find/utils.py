"""
some useful functions
"""

import hashlib
import re
from itertools import groupby
from typing import Callable

from colorama import Cursor
from colorama.ansi import clear_line


def sizeof_fmt(num: float, suffix: str = ""):
    """
    simply display a human readable size
    """
    for unit in ("", "K", "M", "G"):
        if abs(num) < 1024:
            if isinstance(num, float):
                return f"{num:0.1f}{unit}{suffix}"
            return f"{num}{unit}{suffix}"
        num /= 1024.0
    raise ValueError()


def parse_size(sizeHR):
    """Convert human readable sizes to bytes.
    Assumes 1k = 1024 bytes.
    """
    units = {"B": 1, "K": 2**10, "M": 2**20, "G": 2**30, "T": 2**40}

    def split_text(s):
        for k, g in groupby(s, str.isalpha):
            yield "".join(g)

    if not sizeHR[-1].isalpha():
        sizeHR += "B"  # tack a B on the end if its just digits

    digit, unit = split_text(sizeHR.upper())
    if len(unit) > 1:
        unit = unit.rstrip("B")
    return int(float(digit) * units[unit])


def print_temp_message(msg: str):
    """
    print a message and reset the cursor to the begining of the line
    """
    print(clear_line(), msg, Cursor.BACK(len(msg)), sep="", end="", flush=True)


def compute_fingerprint(content, func: Callable = hashlib.md5):
    """
    compute fingerprint given the algo function (sha1, md5 ...)
    """
    algo = func()
    algo.update(content)
    return algo.hexdigest()
