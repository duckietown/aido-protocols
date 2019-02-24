from dataclasses import dataclass
from typing import Tuple, Dict

# Events

ChannelName = str


class Event:
    pass


@dataclass
class InputReceived(Event):
    channel: ChannelName


@dataclass
class OutputProduced(Event):
    channel: ChannelName


# Language over events

class Language:
    pass


@dataclass
class ExpectInputReceived(Language):
    channel: ChannelName


@dataclass
class ExpectOutputProduced(Language):
    channel: ChannelName


@dataclass
class InSequence(Language):
    ls: Tuple[Language, ...]


@dataclass
class ZeroOrOne(Language):
    l: Language


@dataclass
class ZeroOrMore(Language):
    l: Language


@dataclass
class OneOrMore(Language):
    l: Language


@dataclass
class Either(Language):
    ls: Tuple[Language, ...]


# Interaction protocol


@dataclass
class InteractionProtocol:
    # Description
    description: str
    # Type for each input or output
    inputs: Dict[ChannelName, type]
    outputs: Dict[ChannelName, type]
    # The interaction language
    language: str

    # interaction: Language = None

    def __post_init__(self):
        from .language_parse import parse_language, language_to_str
        self.interaction = parse_language(self.language)
        self.language = language_to_str(self.interaction)
