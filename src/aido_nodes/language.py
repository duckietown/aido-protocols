from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Tuple, Dict

# Events

ChannelName = str  # NewType('ChannelName', str)


class Event:
    pass

@dataclass
class InputReceived(Event):
    channel: ChannelName

@dataclass
class OutputProduced(Event):
    channel: ChannelName

class NoMoreEvents(Event):
    pass

@dataclass
class InputClosed(Event):
    channel: ChannelName

@dataclass
class OutputClosed(Event):
    channel: ChannelName


class LanguageNotRecognized(Exception):
    pass


# Language over events

@dataclass
class Language(metaclass=ABCMeta):

    def reset(self):
        pass

    @abstractmethod
    def push(self, x: Event):
        """ Does nothing or raises LanguageNotRecognized """


@dataclass
class ExpectInputReceived(Language):
    channel: ChannelName

    def push(self, x: Event):
        pass  # XXX


@dataclass
class ExpectOutputProduced(Language):
    channel: ChannelName

    def push(self, x: Event):
        pass  # XXX


@dataclass
class InSequence(Language):
    ls: Tuple[Language, ...]

    def push(self, x: Event):
        pass  # XXX


@dataclass
class ZeroOrOne(Language):
    l: Language

    def push(self, x: Event):
        pass  # XXX


@dataclass
class ZeroOrMore(Language):
    l: Language

    def push(self, x: Event):
        pass  # XXX


@dataclass
class OneOrMore(Language):
    l: Language

    def push(self, x: Event):
        pass  # XXX


@dataclass
class Either(Language):
    ls: Tuple[Language, ...]

    def push(self, x: Event):
        pass  # XXX


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
        self.language= language_to_str(self.interaction)

