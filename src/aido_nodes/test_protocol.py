from dataclasses import dataclass
from typing import Sequence, List, Union

from aido_nodes import Language, OutputProduced, InputReceived, Event, ExpectInputReceived, ABCMeta, \
    ExpectOutputProduced, InSequence, ZeroOrMore, NoMoreEvents, abstractmethod, Either, OneOrMore, ZeroOrOne
from aido_nodes.test_language import parse_language

O = OutputProduced
I = InputReceived


class Result:
    pass


class Enough(Result):
    pass


class Unexpected(Result):
    pass


class NeedMore(Result):
    pass


class ProtocolChecker(metaclass=ABCMeta):
    def __init__(self, language: Language):
        self.language = language
        self.stack = []

    @abstractmethod
    def push(self, event: Event) -> Result:
        pass

    @abstractmethod
    def finish(self) -> Union[NeedMore, Enough]:
        pass


@dataclass(repr=False)
class ProtocolCheckerIR(ProtocolChecker):
    l: ExpectInputReceived

    def __post_init__(self):
        self.received = False

    def __repr__(self):
        return f'Expect({self.l})'

    def push(self, event: Event) -> Result:
        if self.received:
            return Unexpected()
        if not isinstance(event, InputReceived):
            return Unexpected()
        if event.channel != self.l.channel:
            return Unexpected()
        self.received = True
        return Enough()

    def finish(self) -> Union[NeedMore, Enough]:
        if self.received:
            return Enough()
        else:
            return NeedMore()


@dataclass(repr=False)
class ProtocolCheckerOP(ProtocolChecker):
    l: ExpectOutputProduced

    def __repr__(self):
        return f'Expect({self.l})'

    def __post_init__(self):
        self.received = False

    def push(self, event: Event) -> Result:
        if self.received:
            return Unexpected()

        if not isinstance(event, OutputProduced):
            return Unexpected()
        if event.channel != self.l.channel:
            return Unexpected()
        self.received = True
        return Enough()

    def finish(self) -> Union[NeedMore, Enough]:
        if self.received:
            return Enough()
        else:
            return NeedMore()


def get_checker(l: Language) -> ProtocolChecker:
    if isinstance(l, ExpectOutputProduced):
        return ProtocolCheckerOP(l)

    if isinstance(l, ExpectInputReceived):
        return ProtocolCheckerIR(l)

    if isinstance(l, InSequence):
        return ProtocolCheckerSequence(l)

    if isinstance(l, ZeroOrMore):
        return ProtocolCheckerZeroOrMore(l)

    if isinstance(l, OneOrMore):
        return ProtocolCheckerOneOrMore(l)

    if isinstance(l, ZeroOrOne):
        return ProtocolCheckerZeroOrOne(l)

    if isinstance(l, Either):
        return ProtocolCheckerEither(l)

    raise NotImplementedError(l)


# @dataclass(repr=False)
class ProtocolCheckerSequence(ProtocolChecker):
    l: InSequence

    def __repr__(self):
        return f'PCSequence({self.to_be_satisfied})'

    def __init__(self, l):
        self.l = l
        self.to_be_satisfied = [get_checker(_) for _ in self.l.ls]

    def push(self, event: Event) -> Result:
        if not self.to_be_satisfied:
            return Unexpected()
        first = self.to_be_satisfied[0]
        res = first.push(event)
        if isinstance(res, Enough):
            self.to_be_satisfied.pop(0)
            if self.to_be_satisfied:
                return NeedMore()
            else:
                return Enough()
        elif isinstance(res, Unexpected):
            return Unexpected()
        elif isinstance(res, NeedMore):
            return NeedMore()
        else:
            assert False

    def finish(self) -> Union[NeedMore, Enough]:
        if self.to_be_satisfied:
            return NeedMore()
        else:
            return Enough()


@dataclass
class ProtocolCheckerEither(ProtocolChecker):
    l: Either

    def __post_init__(self):
        self.to_be_satisfied = {i: get_checker(_) for i, _ in enumerate(self.l.ls)}

    def push(self, event: Event) -> Result:
        enough = None
        need_more = None
        for k, v in list(self.to_be_satisfied.items()):
            res = v.push(event)
            if isinstance(res, Unexpected):
                self.to_be_satisfied.pop(k)
            elif isinstance(res, Enough):
                enough = res
            elif isinstance(res, NeedMore):
                need_more = res

        if enough is not None:
            return enough

        if need_more is not None:
            return need_more

        if not self.to_be_satisfied:
            return Unexpected()

        assert False, self.to_be_satisfied

    def finish(self) -> Union[NeedMore, Enough, Unexpected]:
        if not self.to_be_satisfied:
            return Unexpected()

        enough = None
        for k, v in self.to_be_satisfied.items():
            res = v.finish()
            if isinstance(res, Enough):
                enough = res

        if enough is not None:
            return enough

        return NeedMore()


@dataclass
class ProtocolCheckerZeroOrMore(ProtocolChecker):
    l: ZeroOrMore

    def __post_init__(self):
        self.current = None

    def push(self, event: Event) -> Result:
        if self.current is None:
            self.current = get_checker(self.l.l)

        res = self.current.push(event)
        if isinstance(res, Unexpected):
            return res
        elif isinstance(res, Enough):
            self.current = None
            return Enough()
        elif isinstance(res, NeedMore):
            return res
        else:
            assert False

    def finish(self) -> Union[NeedMore, Enough]:
        if self.current:
            return NeedMore()
        else:
            return Enough()


@dataclass
class ProtocolCheckerOneOrMore(ProtocolChecker):
    l: OneOrMore

    def __post_init__(self):
        self.nfound = 0
        self.current = None

    def push(self, event: Event) -> Result:
        if self.current is None:
            self.current = get_checker(self.l.l)

        res = self.current.push(event)
        if isinstance(res, Unexpected):
            return res
        elif isinstance(res, Enough):
            self.current = None
            self.nfound += 1
            return Enough()
        elif isinstance(res, NeedMore):
            return res
        else:
            assert False

    def finish(self) -> Union[NeedMore, Enough]:
        if self.nfound == 0:
            return NeedMore()

        if self.current:
            return self.current.finish()
        else:
            return Enough()


@dataclass
class ProtocolCheckerZeroOrOne(ProtocolChecker):
    l: ZeroOrOne

    def __post_init__(self):
        self.nfound = 0
        self.current = None

    def push(self, event: Event) -> Result:
        if self.nfound == 1:
            return Unexpected()

        if self.current is None:
            self.current = get_checker(self.l.l)

        res = self.current.push(event)
        if isinstance(res, Unexpected):
            return res
        elif isinstance(res, Enough):
            self.nfound += 1
            return Enough()
        elif isinstance(res, NeedMore):
            return res
        else:
            assert False

    def finish(self) -> Union[NeedMore, Enough]:
        if self.current:
            return self.current.finish()
        else:
            return Enough()


def assert_seq(s: str, seq: List[Event], expect: Sequence[type], final: type):
    l = parse_language(s)
    pc = get_checker(l)
    # all except last
    for i, (e, r) in enumerate(zip(seq, expect)):
        res = pc.push(e)
        if not isinstance(res, r):
            msg = f'Input {i} ({s}) response was {type(res).__name__} instead of {r.__name__}'
            msg += f'\n entire sequence: {seq}'
            msg += f'\n language: {l}'
            raise Exception(msg)

    res = pc.finish()
    if not isinstance(res, final):
        msg = f'finish  response was {type(res).__name__} instead of {final.__name__}'
        msg += f'\n entire sequence: {seq}'
        msg += f'\n language: {l}'
        raise Exception(msg)


def test_proto_out1():
    seq = [OutputProduced("a")]
    assert_seq("out:a", seq, (Enough,), Enough)


def test_proto_in1():
    seq = [InputReceived("a")]
    assert_seq("in:a", seq, (Enough,), Enough)


def test_proto3():
    seq = [InputReceived("a")]
    assert_seq("out:a", seq, (Unexpected,), NeedMore)


def test_proto4():
    seq = [OutputProduced("a")]
    assert_seq("in:a", seq, (Unexpected,), NeedMore)


def test_proto05():
    seq = [InputReceived("b")]
    assert_seq("in:a", seq, (Unexpected,), NeedMore)


def test_proto06():
    seq = [OutputProduced("b")]
    assert_seq("in:a", seq, (Unexpected,), NeedMore)


def test_proto07():
    seq = [OutputProduced("a"), OutputProduced("b")]
    assert_seq("out:a ; out:b", seq, (NeedMore, Enough), Enough)


def test_proto08():
    seq = [OutputProduced("a"), OutputProduced("b")]
    assert_seq("out:a ; out:b ; out:b", seq, (NeedMore, NeedMore), NeedMore)


def test_proto09():
    seq = [OutputProduced("a")]
    assert_seq("out:a ; out:b", seq, (NeedMore,), NeedMore)


def test_proto10():
    seq = [OutputProduced("a"), OutputProduced("b"), OutputProduced("c")]
    assert_seq("out:a ; out:b", seq, (NeedMore, Enough, Unexpected), Enough)


def test_proto_zom_01():
    seq = []
    assert_seq("out:a *", seq, (), Enough)


def test_proto_zom_02():
    seq = [OutputProduced("a")]
    assert_seq("out:a *", seq, (Enough,), Enough)


def test_proto_zom_03():
    seq = [OutputProduced("a"), OutputProduced("a")]
    assert_seq("out:a *", seq, (Enough, Enough), Enough)


def test_proto_either_01():
    seq = [OutputProduced("a")]
    assert_seq("out:a | out:b ", seq, (Enough,), Enough)


def test_proto_either_02():
    seq = [OutputProduced("b")]
    assert_seq("out:a | out:b ", seq, (Enough,), Enough)


def test_proto_either_03():
    seq = [OutputProduced("c")]
    assert_seq("out:a | out:b | out:c ", seq, (Enough,), Enough)


def test_proto_either_04():
    seq = [OutputProduced("a"), OutputProduced("b")]
    assert_seq("(out:a ; out:b) | (out:b ; out:a) ", seq, (NeedMore, Enough), Enough)


def test_proto_either_05():
    seq = [OutputProduced("b"), OutputProduced("a")]
    assert_seq("(out:a ; out:b) | (out:b ; out:a) ", seq, (NeedMore, Enough,), Enough)


def test_proto_oom_01():
    seq = []
    assert_seq("out:a +", seq, (), NeedMore)


def test_proto_oom_02():
    seq = [OutputProduced("a")]
    assert_seq("out:a +", seq, (Enough,), Enough)


def test_proto_oom_03():
    seq = [OutputProduced("a"), OutputProduced("a")]
    assert_seq("out:a +", seq, (Enough, Enough), Enough)


def test_proto_zoom_01():
    seq = []
    assert_seq("out:a ?", seq, (), Enough)


def test_proto_zoom_02():
    seq = [OutputProduced("a")]
    assert_seq("out:a ?", seq, (Enough,), Enough)


def test_proto_zoom_03():
    seq = [OutputProduced("a"), OutputProduced("a")]
    assert_seq("out:a ?", seq, (Enough, Unexpected), Enough)


def test_protocol_complex1():
    l = """
        (
            in:next_episode ; (
                out:no_more_episodes | 
                (out:episode_start ;
                    (in:next_image ; (out:image | out:no_more_images))*)
            )
        )*            
    """
    seq = [InputReceived("next_episode"), OutputProduced("episode_start")]
    assert_seq(l, seq, (NeedMore, Enough), Enough)


def test_protocol_complex1_0():
    l = """
        (
            in:next_episode ; (
                out:no_more_episodes | 
                (out:episode_start ;
                    (in:next_image ; (out:image | out:no_more_images))*)
            )
        )*            
    """
    seq = [InputReceived("next_episode"), OutputProduced("episode_start")]
    assert_seq(l, seq, (NeedMore, Enough), Enough)
