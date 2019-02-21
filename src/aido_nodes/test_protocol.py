from dataclasses import dataclass
from typing import Sequence, List, Union, Tuple, Optional, Set

from networkx.drawing.nx_pydot import write_dot

from aido_nodes import Language, OutputProduced, InputReceived, Event, ExpectInputReceived, ExpectOutputProduced, \
    InSequence, ZeroOrMore, Either, OneOrMore, ZeroOrOne
from aido_nodes.test_language import parse_language
from contracts.utils import indent

O = OutputProduced
I = InputReceived


class Result:
    pass


@dataclass
class Enough(Result):
    pass


@dataclass
class Unexpected(Result):
    msg: str

    def __repr__(self):
        return 'Unexpected:' + indent(self.msg, '  ')


@dataclass
class NeedMore(Result):
    pass


import networkx as nx

NodeName = Tuple[str, ...]


class Always:
    pass


def get_nfa(g: Optional[nx.DiGraph], start_node: NodeName, accept_node: NodeName, l: Language,
            prefix: Tuple[str, ...] = ()) -> nx.DiGraph:
    g.add_node(start_node, label="/".join(start_node))
    g.add_node(accept_node, label="/".join(accept_node))
    if isinstance(l, ExpectOutputProduced):
        g.add_edge(start_node, accept_node, event_match=l, label=f'out-{l.channel}')

    elif isinstance(l, ExpectInputReceived):
        g.add_edge(start_node, accept_node, event_match=l, label=f'in-{l.channel}')
    elif isinstance(l, InSequence):
        current = start_node
        for i, li in enumerate(l.ls):
            if i == len(l.ls) - 1:
                n = accept_node
            else:
                n = prefix + (f'after{i}',)
            g.add_node(n)
            get_nfa(g, start_node=current, accept_node=n, prefix=prefix + (f'{i}',), l=li)
            current = n

    elif isinstance(l, ZeroOrMore):
        g.add_edge(start_node, accept_node, event_match=Always(), label='always')
        get_nfa(g, start_node=accept_node, accept_node=accept_node, l=l.l, prefix=prefix + ('zero_or_more',))

    elif isinstance(l, OneOrMore):
        # start to accept
        get_nfa(g, start_node=start_node, accept_node=accept_node, l=l.l, prefix=prefix + ('one_or_more', '1'))
        # accept to accept
        get_nfa(g, start_node=accept_node, accept_node=accept_node, l=l.l, prefix=prefix + ('one_or_more', '2'))

    elif isinstance(l, ZeroOrOne):
        g.add_edge(start_node, accept_node, event_match=Always(), label='always')
        get_nfa(g, start_node=start_node, accept_node=accept_node, l=l.l, prefix=prefix + ('zero_or_one',))

    elif isinstance(l, Either):
        for i, li in enumerate(l.ls):
            get_nfa(g, start_node=start_node, accept_node=accept_node, l=li, prefix=prefix + (f'either{i}',))
    else:
        assert False, type(l)


def event_matches(l: Language, event: Event):
    if isinstance(l, ExpectInputReceived):
        return isinstance(event, InputReceived) and event.channel == l.channel

    if isinstance(l, ExpectOutputProduced):
        return isinstance(event, OutputProduced) and event.channel == l.channel

    if isinstance(l, Always):
        return False
    raise NotImplementedError(l)


class LanguageChecker:
    g: nx.DiGraph
    active: Set[NodeName]

    def __init__(self, language):
        self.g = nx.MultiDiGraph()
        self.start_node = ('start',)
        self.accept_node = ('accept',)
        get_nfa(g=self.g, l=language, start_node=self.start_node, accept_node=self.accept_node, prefix=())
        # for (a, b, data) in self.g.out_edges(data=True):
        #     print(f'{a} -> {b} {data["event_match"]}')
        write_dot(self.g, 'l.dot')
        self.active = {self.start_node}
        self._evolve_empty()

    def _evolve_empty(self):
        now_active = set()
        for node in self.active:
            nalways = 0
            nother = 0
            for (_, neighbor, data) in self.g.out_edges([node], data=True):
                # print(f'-> {neighbor} {data["event_match"]}')
                if isinstance(data['event_match'], Always):
                    now_active.add(neighbor)
                    nalways += 1
                else:
                    nother += 1
            if nother or (nalways == 0):
                now_active.add(node)

        self.active = now_active

    def push(self, event) -> Result:
        now_active = set()
        # print(f'push: active is {self.active}')
        # print(f'push: considering {event}')
        for node in self.active:
            for (_, neighbor, data) in self.g.out_edges([node], data=True):
                if event_matches(data['event_match'], event):
                    # print(f'now activating {neighbor}')
                    now_active.add(neighbor)
                # else:
                #     print(f"event_match {event} does not match {data['event_match']}")
        #
        # if not now_active:
        #     return Unexpected('')

        self.active = now_active
        # print(f'push: now active is {self.active}')
        self._evolve_empty()
        # print(f'push: now active is {self.active}')
        return self.finish()

    def finish(self) -> Union[NeedMore, Enough, Unexpected]:
        # print(f'finish: active is {self.active}')
        if not self.active:
            return Unexpected('no active')
        if self.accept_node in self.active:
            return Enough()
        return NeedMore()



def assert_seq(s: str, seq: List[Event], expect: Sequence[type], final: type):
    l = parse_language(s)
    pc = LanguageChecker(l)

    # all except last
    for i, (e, r) in enumerate(zip(seq, expect)):
        res = pc.push(e)
        if not isinstance(res, r):
            msg = f'Input {i} ({e}) response was {type(res).__name__} instead of {r.__name__}'
            msg += f'\n entire sequence: {seq}'
            msg += f'\n language: {l}'
            raise Exception(msg)

    res = pc.finish()
    if not isinstance(res, final):
        msg = f'finish response was {type(res).__name__} instead of {final.__name__}'
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
    assert_seq("out:a", seq, (Unexpected,), Unexpected)


def test_proto4():
    seq = [OutputProduced("a")]
    assert_seq("in:a", seq, (Unexpected,), Unexpected)


def test_proto05():
    seq = [InputReceived("b")]
    assert_seq("in:a", seq, (Unexpected,), Unexpected)


def test_proto06():
    seq = [OutputProduced("b")]
    assert_seq("in:a", seq, (Unexpected,), Unexpected)


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
    assert_seq("out:a ; out:b", seq, (NeedMore, Enough, Unexpected), Unexpected)


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
    assert_seq("out:a ?", seq, (Enough, Unexpected), Unexpected)


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
        
            in:next_episode ; (
                out:no_more_episodes | 
                (out:episode_start ;
                    (in:next_image ; (out:image | out:no_more_images))*)
            )
                    
    """
    seq = [InputReceived("next_episode"), OutputProduced("no_more_episodes")]
    assert_seq(l, seq, (NeedMore, Enough), Enough)


def test_protocol_complex1_1():
    l = """

               in:next_episode ; (
                   out:no_more_episodes | 
                   (out:episode_start ;
                       (in:next_image ; (out:image | out:no_more_images))*)
               )

       """
    seq = [InputReceived("next_episode"),
           OutputProduced("episode_start")]
    assert_seq(l, seq, (NeedMore, Enough), Enough)


def test_protocol_complex1_2():
    l = """

               in:next_episode ; (
                   out:no_more_episodes | 
                   (out:episode_start ;
                       (in:next_image ; (out:image | out:no_more_images))*)
               )

       """
    seq = [InputReceived("next_episode"),
           OutputProduced("episode_start"),
           InputReceived("next_image"),
           OutputProduced("image"),
           ]
    assert_seq(l, seq, (NeedMore, Enough), Enough)


def test_protocol_complex1_3():
    l0 = """

        out:episode_start ;
            (in:next_image ; (out:image | out:no_more_images))*

        """
    seq = [OutputProduced("episode_start")]
    assert_seq(l0, seq, (Enough,), Enough)