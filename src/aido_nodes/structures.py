import socket
import time
from dataclasses import dataclass, field
from typing import Optional, Dict

import numpy as np


@dataclass
class Timestamp:
    s: int
    us: int


def timestamp_from_seconds(f: float) -> Timestamp:
    s = int(np.floor(f))
    extra = f - s
    us = int(extra * 1000 * 1000 * 1000)
    return Timestamp(s, us)


@dataclass
class TimeSpec:
    time: Timestamp
    frame: str
    clock: str

    time2: Optional[Timestamp] = None


def local_time() -> TimeSpec:
    s = time.time()
    hostname = socket.gethostname()
    return TimeSpec(time=timestamp_from_seconds(s),
                    frame='epoch',
                    clock=hostname)


@dataclass
class TimingInfo:
    acquired: Optional[Dict[str, TimeSpec]] = field(default_factory=dict)
    processed: Optional[Dict[str, TimeSpec]] = field(default_factory=dict)
    received: Optional[TimeSpec] = None

# T = TypeVar('T')
#
#
# @dataclass
# class Message:
#     topic: str
#     data: Any
#     timing: Optional[TimingInfo]