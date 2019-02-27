from aido_nodes import OutputProduced, Enough, Unexpected
from aido_nodes_tests.test_protocol import assert_seq
from aido_schemas import protocol_image_source
from comptests import comptest


@comptest
def test_proto_image_source():
    l0 = protocol_image_source
    seq = [OutputProduced("next_image")]
    assert_seq(l0, seq, (Unexpected,), Enough)
