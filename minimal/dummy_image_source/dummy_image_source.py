#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Tuple, ClassVar
from aido_nodes import JPGImage
import numpy as np

from aido_nodes.protocols import protocol_image_source, InteractionProtocol
from aido_nodes.wrapper import wrap_direct


# noinspection PyUnresolvedReferences
@dataclass
class DummyImageSourceConfig:
    """
        Configuration for the node.

        :param shape: Image shape in Numpy conventions (height, width).
        :param images_per_episode: Number of images for each episode.
        :param num_episodes: Number of episodes in total.
    """
    shape: Tuple[int, int] = (480, 640)
    images_per_episode: int = 120
    num_episodes: int = 10

@dataclass
class DummyImageSourceState:
    """
        State for the node.
    """
    episode: int = -1
    nimages: int = -1

@dataclass
class DummyImageSource:
    config: DummyImageSourceConfig = field(default_factory=DummyImageSourceConfig)
    state: DummyImageSourceState = field(default_factory=DummyImageSourceState)
    protocol: ClassVar[InteractionProtocol] = protocol_image_source

    def init(self):
        self.state.episode = -1
        self.state.nimages = -1

    def on_updated_config(self, context, key, value):
        context.log(f'Config was updated: {key} = {value!r}')

    def on_received_next_episode(self, context):
        self._start_episode(context)

    def on_received_next_image(self, context):
        if self.state.nimages >= self.config.images_per_episode:
            context.write('no_more_images', None)
            return

        H, W = self.config.shape
        values = (128 + np.random.randn(H, W, 3) * 60).astype('uint8')
        jpg_data = bgr2jpg(values)
        image = JPGImage(jpg_data)
        context.write('image', image)

    def _start_episode(self, context):
        if self.state.episode >= self.config.num_episodes:
            context.write('no_more_episodes', None)
            return
        self.state.episode += 1
        self.state.nimages = 0
        es = dict(episode_name=f'episode{self.state.episode}')
        context.write('episode_start', es)


def bgr2jpg(image_cv) -> bytes:
    import cv2
    # noinspection PyUnresolvedReferences
    compress = cv2.imencode('.jpg', image_cv)[1]
    jpg_data = np.array(compress).tostring()
    return jpg_data


def main():

    import sys
    agent = DummyImageSource()
    wrap_direct(agent=agent, protocol=agent.protocol, args=sys.argv[1:])


if __name__ == '__main__':
    main()
