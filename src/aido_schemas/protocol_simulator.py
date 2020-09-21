from dataclasses import dataclass
from typing import Dict, Optional

import numpy as np

from zuper_typing.literal import make_Literal  # XXX
from .basics import InteractionProtocol
from .protocol_agent import EpisodeStart

RobotName = str

__all__ = [
    "RobotState",
    "RobotName",
    "RobotObservations",
    "RobotInterfaceDescription",
    "RobotConfiguration",
    "RobotPerformance",
    "ScenarioRobotSpec",
    "SetRobotCommands",
    "GetRobotObservations",
    "GetRobotState",
    "Metric",
    "PerformanceMetrics",
    "protocol_simulator",
    "protocol_scenario_maker",
    "SetMap",
    "SpawnRobot",
    "Step",
    "SimulationState",
    "Scenario",
    "StateDump",
    "JPGImage",
    "DumpState",
]


@dataclass
class JPGImage:
    """
        An image in JPG format.

        jpg_data: Bytes of a JPG file
    """

    jpg_data: bytes


@dataclass
class SetMap:
    map_data: object


@dataclass
class RobotConfiguration:
    pose: np.ndarray
    velocity: np.ndarray


@dataclass
class SetRobotCommands:
    robot_name: RobotName
    t_effective: float
    commands: object


@dataclass
class GetRobotObservations:
    robot_name: RobotName
    t_effective: float


@dataclass
class GetRobotState:
    robot_name: RobotName
    t_effective: float


@dataclass
class RobotObservations:
    robot_name: RobotName
    t_effective: float
    observations: object


@dataclass
class RobotState:
    robot_name: RobotName
    t_effective: float
    state: object


@dataclass
class SimulationState:
    """
        Returns the simulation state.

        done: Whether the simulation should be terminated.
        done_why: Human-readable short message.
        done_code: Short string to use as code for statistics.
    """

    done: bool
    done_why: Optional[str]
    done_code: Optional[str]


@dataclass
class Metric:
    higher_is_better: bool
    cumulative_value: float
    description: str

    def __post_init__(self):
        if isinstance(self.cumulative_value, int):
            self.cumulative_value = float(self.cumulative_value)


@dataclass
class PerformanceMetrics:
    """
        Performance metrics for an agent.

        By convention there will be one called "reward" for RL tasks.

        Note that the values are *cumulative* to make it possible to have
        a sampling-invariant behavior.
    """

    metrics: Dict[str, Metric]


@dataclass
class RobotPerformance:
    robot_name: RobotName
    t_effective: float
    performance: PerformanceMetrics


@dataclass
class RobotInterfaceDescription:
    robot_name: RobotName
    observations: type
    commands: type


@dataclass
class Step:
    until: float


@dataclass
class DumpState:
    pass


@dataclass
class StateDump:
    """ Opaque object that contains the simulator's state, whichever it is. """

    state: object


MOTION_PARKED = "parked"
MOTION_MOVING = "moving"
NPMotion = make_Literal(MOTION_PARKED, MOTION_MOVING)


@dataclass
class ScenarioRobotSpec:
    description: str
    playable: bool
    configuration: RobotConfiguration

    # if not playable
    motion: Optional[NPMotion]


@dataclass
class SpawnRobot:
    playable: bool
    robot_name: RobotName
    configuration: RobotConfiguration
    motion: Optional[NPMotion]


@dataclass
class Scenario:
    # Specification of the environments
    scenario_name: str
    environment: object
    robots: Dict[str, ScenarioRobotSpec]


description = """\

A "scenario maker" is an object that is able to create robot simulations scenarios.

Each scenario contains:

- The definition of a map and other environmental conditions.
- The pose of the "playing" robot. 


A scenario maker can be random. In that case it must give the same sequence
for the same values of the seed. 

"""

protocol_scenario_maker = InteractionProtocol(
    description=description,
    language="""\
        in:seed? ;
        (
            in:next_scenario ; 
            (out:finished | out:scenario)
        )*
""",
    inputs={
        # Seed random number generator
        "seed": int,
        "next_scenario": type(None),
    },
    outputs={"finished": type(None), "scenario": Scenario},
)
description = """\

Interface to be implemented by a simulator.

Logical API:

`simulator.clear(reset_info)`

Resets the simulation data. Need to re-transmit map and robot poses.

`simulator.set_map(map)`

Sets the map to use.

`simulator.spawn_robot(name, configuration)`

Adds a robot to the simulation of the given name.

`simulator.episode_start`

`simulator.step(until: timestamp)`

Steps the simulation until the given timestamp.


`simulator.set_robot_commands(t: timestamp, commands)`

Steps the simulation until the given timestamp.

`simulator.get_robot_observations(name, t: timestamps)`

Asks for the dump of a robot state.

`simulator.dump_robot_state(name)`

Asks for the dump of a robot state.


`seed(int)`

Sets seed for random process.


    """

protocol_simulator = InteractionProtocol(
    description=description,
    language="""\
        
        in:seed? ;
            (
            in:clear ; 
            in:set_map ;
            (in:spawn_robot)*;
            
            (in:get_robot_interface_description; out:robot_interface_description)*;
            
            in:episode_start;
                
                (
                    in:step |
                    in:set_robot_commands |
                    (in:get_robot_observations ;  out:robot_observations) |
                    (in:get_robot_performance ;  out:robot_performance) |
                    (in:get_robot_state ;  out:robot_state) |
                    (in:get_sim_state ;  out:sim_state) |
                    (in:dump_state   ;  out:state_dump) |
                    (in:get_ui_image ; out:ui_image) 
                )* 
        )*
""",
    inputs={
        # Seed random number generator
        "seed": int,
        "clear": type(None),
        "set_map": SetMap,
        "spawn_robot": SpawnRobot,
        "get_robot_interface_description": RobotName,
        "get_robot_performance": RobotName,
        "get_sim_state": type(None),
        "episode_start": EpisodeStart,
        # Step physics
        "step": Step,
        "set_robot_commands": SetRobotCommands,
        "get_robot_observations": GetRobotObservations,
        "get_robot_state": GetRobotState,
        "get_ui_image": type(None),
        # Dump state information
        "dump_state": DumpState,
    },
    outputs={
        "robot_observations": RobotObservations,
        "robot_state": RobotState,
        "robot_performance": RobotPerformance,
        "robot_interface_description": RobotInterfaceDescription,
        "sim_state": SimulationState,
        "state_dump": StateDump,
        "ui_image": JPGImage,
    },
)

protocol_scorer = InteractionProtocol(
    description="""Protocol for scorer""",
    language="""\
            in:set_map ;
            (
                in:episode_start;
                (
                    in:set_sim_state |
                    in:set_robot_state |
                    (in:get_robot_performance; out:robot_performance)
                )*
            )*
""",
    inputs={
        "set_map": SetMap,
        "episode_start": EpisodeStart,
        "set_robot_state": RobotState,
        "set_sim_state": SimulationState,
        "get_robot_performance": RobotName,
    },
    outputs={"robot_performance": RobotPerformance},
)
