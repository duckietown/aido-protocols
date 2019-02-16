from aido_nodes import JPGImage, PWMCommands, Seed
from .language import ZeroOrMore, InSequence, ExpectInputReceived, \
    ExpectOutputProduced, InteractionProtocol, ZeroOrOne

protocol_agent_jpg_pwm = InteractionProtocol(
        description="""

Receives a DistortedImage, to which
it replies with PWMCommands.

    """,
        inputs={
            "camera_image": JPGImage,
        },
        outputs={
            "pwm_commands": PWMCommands,
        },
        interaction=ZeroOrMore(
                InSequence(
                        (ExpectInputReceived("camera_image"),
                         ExpectOutputProduced("pwm_commands")
                         )
                )
        )
)

protocol_image_filter = InteractionProtocol(
        description="""
An image filter. 
    """,
        inputs={
            "image": JPGImage,
        },
        outputs={
            "transformed": JPGImage,
        },
        interaction=ZeroOrMore(
                InSequence(
                        (ExpectInputReceived("image"),
                         ExpectOutputProduced("transformed")
                         )
                )
        )
)

interaction_seed = ZeroOrOne(ExpectInputReceived("seed"))

#
#   seed? (in:reset out:reset-ack)
#                ((in:set_commands  out:commands_ack) |
#                 (in:step_physics  out:step_physics_ack) |
#                 (in:dump_state    out:state_dump) |
#                 (in:render        out:image) |
#                 (in:reset         out:reset-ack)* )
#

simulator_protocol = InteractionProtocol(
        description="""\


    """,
        inputs={
            "commands": PWMCommands,
            # Seed random number generator
            "seed": Seed,
            # Reset request
            "reset": str,
            # Render request - produces image
            "render_image": str,
            # Step physics
            "step_physics": Timestamp,
            # Dump state information
            "dump_state": Timestamp,
        },
        outputs={
            "image": JPGImage,
            "commands_ack": None,
            "state_dump": StateDump,
            "reset_ack": StateDump,
            "step_physics_ack": StepPhysicsACK,
        },
        interaction=...

)

renderer_protocol = InteractionProtocol(
        description="""\


    """,
        inputs={
            "map_set": PWMCommands,
            # Seed random number generator
            "seed": Seed,
            # Reset request
            "reset": str,
            # Render request - produces image
            "render_image": RequestRender,

        },
        outputs={
            "image": JPGImage,

        },
        interaction=...

)
