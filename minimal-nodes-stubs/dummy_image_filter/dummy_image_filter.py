#!/usr/bin/env python3
from aido_nodes import JPGImage, wrap_direct
from aido_nodes.protocols import protocol_image_filter

class DummyImageFilter:
    protocol = protocol_image_filter

    def init(self, context):
        context.log('init()')

    def on_received_image(self, context, data: JPGImage):
        transformed = data
        context.write('transformed', transformed)

    def finish(self, context):
        context.log('finish()')



def main():
    import sys
    agent = DummyImageFilter()
    wrap_direct(agent=agent, protocol=agent.protocol, args=sys.argv[1:])

if __name__ == '__main__':
    main()
