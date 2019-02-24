from nose.tools import assert_equal

from aido_nodes import Language, ExpectInputReceived, ExpectOutputProduced, InSequence, ZeroOrMore, ZeroOrOne, \
    OneOrMore, Either
from aido_nodes.language_parse import Syntax
from comptests import comptest
from contracts import check_isinstance


def parse_language(s: str) -> Language:
    expr = Syntax.language
    res = expr.parseString(s, parseAll=True)
    res = res[0]
    return res


def expect_parse(expr, s, expected):
    check_isinstance(s, str)
    check_isinstance(expected, (type(None), Language))
    res = expr.parseString(s, parseAll=True)

    res = res[0]
    print(f'Obtained: {res}')
    print(f'Expected: {expected}')
    if expected:
        assert_equal(res, expected)

@comptest
def test_parse_language_01():
    s = "in:name"
    e = ExpectInputReceived("name")
    expect_parse(Syntax.input_received, s, e)
    expect_parse(Syntax.language, s, e)

@comptest
def test_parse_language_02():
    s = "out:name"
    e = ExpectOutputProduced("name")
    expect_parse(Syntax.output_produced, s, e)

@comptest
def test_parse_language_03():
    s = "out:first ; in:second"
    e = InSequence((ExpectOutputProduced("first"),
                    ExpectInputReceived("second")))
    expect_parse(Syntax.language, s, e)

@comptest
def test_parse_language_04():
    s = "(out:first)*"
    e = ZeroOrMore(ExpectOutputProduced("first"))
    expect_parse(Syntax.language, s, e)

@comptest
def test_parse_language_05():
    s = "(out:first)?"
    e = ZeroOrOne(ExpectOutputProduced("first"))
    expect_parse(Syntax.language, s, e)

@comptest
def test_parse_language_06():
    s = "(out:first)+"
    e = OneOrMore(ExpectOutputProduced("first"))
    expect_parse(Syntax.language, s, e)

@comptest
def test_parse_language_07():
    s = "out:first | out:second"
    e = Either((ExpectOutputProduced("first"), ExpectOutputProduced("second")))
    expect_parse(Syntax.language, s, e)

    s2 = "(out:first | out:second)"
    expect_parse(Syntax.language, s2, e)

@comptest
def test_parse_language_08():
    s = """
                (
                    in:next_episode ; (
                        out:no_episodes | 
                        (out:episode_start ;
                            (in:next_image ; (out:image | out:episode_end))*)
                    )
                )*            
            """

    expect_parse(Syntax.language, s, None)

#
# def test_parse_language_08():
#     s = """
#                 (
#                     in:next_episode ; (
#                         out:no_episodes |
#                         (out:episode_start ;
#                             (in:next_image ; (out:image | out:episode_end))*)
#                     )
#                 )*
#             """
#
#     expect_parse(Syntax.language, s, None)
