from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import NewType, Tuple, Dict, Type, Any

# Events

ChannelName = str #NewType('ChannelName', str)
class Event:
    pass

class InputReceived(Event):
    channel: ChannelName

class OutputProduced(Event):
    channel: ChannelName

class InputClosed(Event):
    pass

class OutputClosed(Event):
    pass

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
        pass # XXX

@dataclass
class ExpectOutputProduced(Language):
    channel: ChannelName

    def push(self, x: Event):
        pass # XXX

@dataclass
class InSequence(Language):
    ls: Tuple[Language, ...]

    def push(self, x: Event):
        pass # XXX

@dataclass
class ZeroOrOne(Language):
    l: Language

    def push(self, x: Event):
        pass # XXX

@dataclass
class ZeroOrMore(Language):
    l: Language

    def push(self, x: Event):
        pass # XXX

@dataclass
class OneOrMore(Language):
    l: Language

    def push(self, x: Event):
        pass # XXX

@dataclass
class Either(Language):
    ls: Tuple[Language, ...]

    def push(self, x: Event):
        pass # XXX

# Interaction protocol

@dataclass
class InteractionProtocol:
    # Description
    description: str
    # Type for each input or output
    inputs: Dict[ChannelName, type]
    outputs: Dict[ChannelName, type]
    # The interaction language
    interaction: Language
