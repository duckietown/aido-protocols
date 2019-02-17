from aido_nodes import JPGImage, PWMCommands, EpisodeStart
from aido_nodes.language_parse import parse_language
from .language import InteractionProtocol

protocol_agent_jpg_pwm = InteractionProtocol(
        description="""

Receives a DistortedImage, to which
it replies with PWMCommands.

    """,
        inputs={"camera_image": JPGImage},
        outputs={"pwm_commands": PWMCommands},
        interaction=parse_language("""
            (in:camera_image ; out:pwm_commands)*
        """)
)

protocol_image_filter = InteractionProtocol(
        description="""An image filter. Takes an image, returns an image.""",
        inputs={"image": JPGImage},
        outputs={"transformed": JPGImage},
        interaction=parse_language(" (in:image ; out:transformed)*")
)

protocol_image_source = InteractionProtocol(
        description="""

An abstraction over logs. 

It emits a series of EpisodeStart followed by a set of images.

    """,
        inputs={"next_image": type(None),
                "next_episode": type(None)},
        outputs={"image": JPGImage,
                 "episode_start": EpisodeStart,
                 "no_more_images": type(None),
                 "no_more_episodes": type(None)},
        interaction=parse_language("""
                (
                    in:next_episode ; (
                        out:no_more_episodes | 
                        (out:episode_start ;
                            (in:next_image ; (out:image | out:no_more_images))*)
                    )
                )*            
            """),
)
