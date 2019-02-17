from dataclasses import dataclass


@dataclass
class PWMCommands:
    """
        PWM commands are floats between 0 and 1.
    """
    motor_left: float
    motor_right: float

@dataclass
class WheelsCmd:
    """ Kinematic wheels commands. Radiants per second. """
    vel_left: float
    vel_right: float


@dataclass
class JPGImage:
    """ An image in JPG format. """
    data: bytes


@dataclass
class EpisodeStart:
    """ Marker for the start of an episode. """
    episode_name: str

@dataclass
class Timestamp:
    pass


@dataclass
class Seed:
    """ Used for describing an RNG seed. """
    seed: int



@dataclass
class StateDump:
    pass


@dataclass
class StepPhysicsACK:
    pass



class RequestRender:
    pass


