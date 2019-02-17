import base64
from dataclasses import dataclass
from typing import Tuple

import numpy as np


@dataclass
class DummyImageSourceConfig:
    """
        :param shape: Image shape in Numpy conventions (height width).
        :param images_per_episode: number of images for each episode.
        :param num_episodes: Number of episodes in total.
    """
    shape: Tuple[int, int] = (480, 640)
    images_per_episode: int = 120
    num_episodes: int = 10


class DummyImageSource:
    config: DummyImageSourceConfig

    episode: int
    nimages: int

    def __init__(self, config: DummyImageSourceConfig = DummyImageSourceConfig()):
        self.config = config

    def init(self):
        self.episode = -1
        self.nimages = -1

    def on_updated_config(self, context, key, value):
        context.log(f'Config was updated: {key} = {value!r}')

    def on_received_next_episode(self, context):
        self._start_episode(context)

    def on_received_next_image(self, context):
        if self.nimages >= self.config.images_per_episode:
            context.write('no_more_images', None)
            return

        H, W = self.config.shape

        values = (np.random.randn(H, W, 3) * 255).astype('uint8')
        jpg_data = bgr2jpg(values)
        image = dict(jpg_data=encode_bytes_as_json(jpg_data))
        context.write('image', image)

    def _start_episode(self, context):
        if self.episode >= self.config.num_episodes:
            context.write('no_more_episodes', None)
            return
        self.episode += 1
        self.nimages = 0

        es = dict(episode_name='episode{self.episode}')
        context.write('episode_start', es)


import cv2


def bgr2jpg(image_cv) -> bytes:
    # noinspection PyUnresolvedReferences
    compress = cv2.imencode('.jpg', image_cv)[1]
    jpg_data = np.array(compress).tostring()
    return jpg_data

def encode_bytes_as_json(b: bytes) -> dict:
    res = {}
    res['base64'] = base64.b64encode(b).decode('ascii')
    return res
