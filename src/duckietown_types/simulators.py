from dataclasses import dataclass
from typing import Tuple

from duckietown_types.language import ZeroOrMore, InSequence, ExpectInputReceived, \
    ExpectOutputProduced, ChannelName, InteractionProtocol, ZeroOrOne


class PWMCommands:
    """
        Both between 0 and 1.
    """
    motor_left: float
    motor_right: float


@dataclass
class WheelsCmd:
    """ Kinematic wheels commands """
    vel_left: float
    vel_right: float


class Image:
    shape: Tuple[int, int]
    data: bytes


class DistortedImage(Image):
    pass


agent_protocol1 = InteractionProtocol(
        description="""
        Receives a DistortedImage, to which
        it replies with PWMCommands.
    """,
        inputs={
            ChannelName("image"): DistortedImage,
        },
        outputs={
            ChannelName("commands"): PWMCommands,
        },
        interaction=ZeroOrMore(
                InSequence(
                        (ExpectInputReceived(ChannelName("image")),
                         ExpectOutputProduced(ChannelName("commands"))
                         )
                )
        )
)


class Timestamp:
    pass


class Seed:
    seed: int


interaction_seed = ZeroOrOne(ExpectInputReceived(ChannelName("seed")))

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
            ChannelName("commands"): PWMCommands,
            # Seed random number generator
            ChannelName("seed"): Seed,
            # Reset request
            ChannelName("reset"): str,
            # Render request - produces image
            ChannelName("render_image"): str,
            # Step physics
            ChannelName("step_physics"): Timestamp,
            # Dump state information
            ChannelName("dump_state"): Timestamp,
        },
        outputs={
            ChannelName("image"): DistortedImage,
            ChannelName("commands_ack"): None,
            ChannelName("state_dump"): StateDump,
            ChannelName("reset_ack"): StateDump,
            ChannelName("step_physics_ack"): StepPhysicsACK,

        },
        interaction=...

)




renderer_protocol = InteractionProtocol(
        description="""\


    """,
        inputs={
            ChannelName("map_set"): PWMCommands,
            # Seed random number generator
            ChannelName("seed"): Seed,
            # Reset request
            ChannelName("reset"): str,
            # Render request - produces image
            ChannelName("render_image"): RequestRender(img),

        },
        outputs={
            ChannelName("image"): DistortedImage,

        },
        interaction=...

)
