from dataclasses import dataclass

from . import InteractionProtocol

__all__ = ["EpisodeStart", "protocol_agent"]


@dataclass
class EpisodeStart:
    """ Marker for the start of an episode. """

    episode_name: str


@dataclass
class GetCommands:
    at_time: float


protocol_agent = InteractionProtocol(
    description="""

Generic protocol for an agent that receives "observations" and responds 
with "commands".

"episode_start" marks the beginning of an episode.  

    """.strip(),
    inputs={
        "observations": object,
        "seed": int,
        "get_commands": GetCommands,
        "episode_start": EpisodeStart,
    },
    outputs={"commands": object},
    language="""
            in:seed? ;
            (   in:episode_start ; 
                (in:observations | 
                    (in:get_commands ; out:commands)
                 )* 
            )*
        """,
)
