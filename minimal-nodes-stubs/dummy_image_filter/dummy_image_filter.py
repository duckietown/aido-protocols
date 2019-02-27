#!/usr/bin/env python3
from aido_node_wrapper import wrap_direct
from aido_schemas import protocol_image_filter, JPGImage

class DummyImageFilter:

    def init(self, context):
        context.log('init()')

    def on_received_image(self, context, data: JPGImage):
        transformed = data
        context.write('transformed', transformed)

    def finish(self, context):
        context.log('finish()')



def main():
    node = DummyImageFilter()
    protocol = protocol_image_filter
    wrap_direct(node=node, protocol=protocol)

if __name__ == '__main__':
    main()
