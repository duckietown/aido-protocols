from typing import Sequence, List

from aido_nodes import OutputProduced, InputReceived, Event
from aido_nodes.language_recognize import LanguageChecker, Enough, Unexpected, NeedMore
from aido_nodes.test_language import parse_language




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
