from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import NewType, Tuple, Dict



# Events

ChannelName = NewType('ChannelName', str)
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

class Language(metaclass=ABCMeta):
    @abstractmethod
    def reset(self):
        pass

    @abstractmethod
    def push(self, x: Event):
        """ Does nothing or raises LanguageNotRecognized """

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
    interaction: Language
