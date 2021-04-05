from aido_schemas import protocol_image_source
from zuper_nodes import OutputProduced, Unexpected
from zuper_nodes_tests.test_protocol import assert_seq


def test_proto_image_source():
    l0 = protocol_image_source.language
    seq = [OutputProduced("next_image")]
    assert_seq(l0, seq, (Unexpected,), Unexpected)
