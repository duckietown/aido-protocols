from dataclasses import dataclass
from typing import Optional, Dict, TypeVar, Generic


@dataclass
class Timestamp:
    s: int
    us: int


@dataclass
class TimeSpec:
    time: Timestamp
    time2: Optional[Timestamp]
    frame: str
    clock: str


def local_time() -> TimeSpec:
    pass


@dataclass
class TimingInfo:
    acquired: Optional[Dict[str, TimeSpec]]
    processed: Optional[Dict[str, TimeSpec]]
    received: Optional[TimeSpec] = None


# T = TypeVar('T')
#
#
# @dataclass
# class Message:
#     topic: str
#     data: Any
#     timing: Optional[TimingInfo]
