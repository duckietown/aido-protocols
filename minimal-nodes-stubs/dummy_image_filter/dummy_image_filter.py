#!/usr/bin/env python3
from aido_schemas import protocol_image_filter, JPGImage, EpisodeStart, wrap_direct, Context


class DummyImageFilter:

    def init(self, context: Context):
        context.info('init()')

    def on_received_episode_start(self, context: Context, data: EpisodeStart):
        context.write('episode_start', data=data)

    def on_received_image(self, context: Context, data: JPGImage):
        transformed = data
        context.write('image', transformed)

    def finish(self, context: Context):
        context.info('finish()')


def main():
    node = DummyImageFilter()
    protocol = protocol_image_filter
    wrap_direct(node=node, protocol=protocol)


if __name__ == '__main__':
    main()
