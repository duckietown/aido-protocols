from aido_nodes import InteractionProtocol
from aido_schemas import JPGImage, PWMCommands, EpisodeStart

protocol_agent_jpg_pwm = InteractionProtocol(
        description="""

Receives a DistortedImage, to which
it replies with PWMCommands.

    """,
        inputs={"camera_image": JPGImage,
                "episode_start": EpisodeStart},
        outputs={"pwm_commands": PWMCommands},
        language="""
            (in:episode_start ; (in:camera_image ; out:pwm_commands)*)*
        """
)

protocol_image_filter = InteractionProtocol(
        description="""An image filter. Takes an image, returns an image.""",
        inputs={"image": JPGImage,
                "episode_start": EpisodeStart},
        outputs={"image": JPGImage,
                 "episode_start": EpisodeStart},
        language="""
        (in:episode_start ; out:episode_start ; (in:image ; out:image)*)*
        """
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
        language="""
                (
                    in:next_episode ; (
                        out:no_more_episodes | 
                        (out:episode_start ;
                            (in:next_image ; (out:image | out:no_more_images))*)
                    )
                )*            
            """,
)
