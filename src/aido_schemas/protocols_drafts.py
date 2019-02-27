from aido_nodes import JPGImage, PWMCommands, Seed, Timestamp, StateDump, StepPhysicsACK, RequestRender
from aido_nodes.language_parse import parse_language
from aido_nodes.language import InteractionProtocol


renderer_protocol = InteractionProtocol(
        description="",
        inputs={
            "map_set": ...,
            # Seed random number generator
            "seed": Seed,
            # Reset request
            "reset": type(None),
            # Render request - produces image
            "render_image": RequestRender,
        },
        outputs={"image": JPGImage},
        interaction=...
)

DuckietownMap = Any
RobotName = str
Pose = Any  # TODO


@dataclass
class SetRobotPose:
    name: RobotName
    pose: Pose


@dataclass
class Result:
    """ Result of an operation. """
    success: bool
    message: Optional[str]


simulator_protocol = InteractionProtocol(
        description="""\

Interface to be implemented by a simulator.

Logical API:


`simulator.set_map(map)`

Sets the map to use.

`simulator.spawn_robot(name)`

Adds a robot to the simulation of the given name.

`simulator.set_robot_pose(name, pose)`

Sets a robot's pose.

`simulator.set_robot_dynamics(name, params)`

`simulator.set_robot_extrinsics(name, params)`

`simulator.set_robot_intrinsics(name, params)`

`simulator.step(until: timestamp)`

Steps the simulation until the given timestamp.

`simulator.clear(t0: timestamp)`

Resets the simulation data. Need to re-transmit map and robot poses.

`simulator.set_robot_commands(t: timestamp, commands)`

Steps the simulation until the given timestamp.

`simulator.get_robot_observations(name, t: timestamps)`

Asks for the dump of a robot state.

`simulator.dump_robot_state(name)`

Asks for the dump of a robot state.


`seed(int)`

Sets seed for random process.


    """,
        language="""\
    in:seed? ;
    in:next_episode ; out:episode_start ;
    (
        (in:set_commands ;  out:commands_ack) |
        (in:step_physics ;  out:step_physics_ack) |
        (in:dump_state   ;  out:state_dump) |
        (in:render       ;  out:image) |
        (in:next_episode ;  out:episode_start) 
    )*
""",
        inputs={
            # Seed random number generator
            "seed": int,
            "set_map": DuckietownMap,
            "spawn_robot": SpawnRobot,
            "set_robot_pose": ...,
            "step": ...,
            "clear": ...,
            "set_robot_commands": PWMCommands,

            # Reset request
            "reset": type(None),
            # Render request - produces image
            "render_image": type(None),
            # Step physics
            "step_physics": float,
            # Dump state information
            "dump_state": float,
        },
        outputs={
            "seed_ack": Result,
            "set_map_ack": Result,
            "spawn_robot_ack": type(None),

            "image": JPGImage,
            "state_dump": Any,
            "reset_ack": type(None),
            "step_physics_ack": type(None),
            "episode_start": EpisodeStart,
        },
)
