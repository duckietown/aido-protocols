from typing import Any

from aido_nodes import InteractionProtocol

BasicProtocol = InteractionProtocol(
        description="""\

Basic interaction protocol for nodes spoken by the node wrapper.

    """,
        inputs={
            "describe_node": type(None),
            "describe_config": type(None),
            "set_config": Any,  # XXX
            "get_state": type(None),
        },
        outputs={
            "node_config_state": Any,
            'node_description': Any,
            'node_state': Any,
            'logs': Any,
            'set_config_ack': type(None),
        },
        language="""\
    (
        (in:describe_node   ;  out:node_description) |
        (in:describe_config ;  out:node_config_state) |
        (in:set_config      ;  out:set_config_ack)  
    )*
""")
