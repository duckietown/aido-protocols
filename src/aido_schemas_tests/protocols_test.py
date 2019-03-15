from aido_schemas import protocol_image_source
from comptests import comptest
from zuper_nodes import OutputProduced, Enough, Unexpected
from zuper_nodes_tests.test_protocol import assert_seq


@comptest
def test_proto_image_source():
    l0 = protocol_image_source
    seq = [OutputProduced("next_image")]
    assert_seq(l0, seq, (Unexpected,), Enough)


@comptest
def test_run_docker0():
    pass


@comptest
def test_run_docker1():
    pass


@comptest
def test_run_docker2():
    pass


@comptest
def test_run_docker3():
    pass


@comptest
def test_run_docker4():
    pass


@comptest
def test_run_docker5():
    pass


@comptest
def test_run_docker6():
    pass


@comptest
def test_run_docker7():
    pass
