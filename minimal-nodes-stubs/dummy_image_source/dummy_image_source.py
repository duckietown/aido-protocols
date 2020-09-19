#!/usr/bin/env python3
from dataclasses import dataclass, field
from typing import Tuple

# noinspection PyUnresolvedReferences
import cv2
import numpy as np


from aido_schemas import protocol_image_source, JPGImage, EpisodeStart, wrap_direct, Context


# noinspection PyUnresolvedReferences
from zuper_nodes.structures import timestamp_from_seconds, TimeSpec, TimingInfo


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

    episode_name: str = None


@dataclass
class DummyImageSource:
    """ A simple example of an image source """

    config: DummyImageSourceConfig = field(default_factory=DummyImageSourceConfig)
    state: DummyImageSourceState = field(default_factory=DummyImageSourceState)

    def init(self):
        self.state.episode = -1
        self.state.nimages = -1

    def on_updated_config(self, context: Context, key: str, value):
        context.info(f"Config was updated: {key} = {value!r}")

    def on_received_next_episode(self, context: Context):
        self._start_episode(context)

    def on_received_next_image(self, context: Context):
        if self.state.nimages >= self.config.images_per_episode:
            context.write("no_more_images", None)
            return

        H, W = self.config.shape
        values = (128 + np.random.randn(H, W, 3) * 60).astype("uint8")
        jpg_data = bgr2jpg(values)
        image = JPGImage(jpg_data)
        delta = 0.15
        t = self.state.nimages * delta
        time = timestamp_from_seconds(t)
        ts = TimeSpec(time=time, frame=self.state.episode_name, clock=context.get_hostname())
        acquired = {"image": ts}
        timing = TimingInfo(acquired=acquired)
        context.write(topic="image", data=image, timing=timing)

    def finish(self):
        pass

    def _start_episode(self, context: Context):
        if self.state.episode >= self.config.num_episodes:
            context.write("no_more_episodes", None)
            return

        self.state.episode += 1
        self.state.nimages = 0
        self.state.episode_name = f"episode{self.state.episode}"

        context.write("episode_start", EpisodeStart(self.state.episode_name))


def bgr2jpg(image_cv) -> bytes:

    compress = cv2.imencode(".jpg", image_cv)[1]
    jpg_data = np.array(compress).tobytes()
    return jpg_data


def main():
    node = DummyImageSource()
    protocol = protocol_image_source
    wrap_direct(node=node, protocol=protocol)


if __name__ == "__main__":
    main()
