from aido_nodes import JPGImage, PWMCommands, Seed, Timestamp, StateDump, StepPhysicsACK, RequestRender
from aido_nodes.language_parse import parse_language
from aido_nodes.language import InteractionProtocol

simulator_protocol = InteractionProtocol(
        description="""\


    """,
        inputs={
            "commands": PWMCommands,
            # Seed random number generator
            "seed": Seed,
            # Reset request
            "reset": type(None),
            # Render request - produces image
            "render_image": type(None),
            # Step physics
            "step_physics": Timestamp,
            # Dump state information
            "dump_state": Timestamp,
        },
        outputs={
            "image": JPGImage,
            "commands_ack": type(None),
            "state_dump": StateDump,
            "reset_ack": StateDump,
            "step_physics_ack": StepPhysicsACK,
        },
        interaction=parse_language("""\
    in:seed? ;
    in:next_episode ; out:episode_start ;
    (
        (in:set_commands ;  out:commands_ack) |
        (in:step_physics ;  out:step_physics_ack) |
        (in:dump_state   ;  out:state_dump) |
        (in:render       ;  out:image) |
        (in:next_episode ;  out:episode_start) 
    )*
""")

)

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
