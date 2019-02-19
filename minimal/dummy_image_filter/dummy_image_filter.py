from aido_nodes import JPGImage
from aido_nodes.protocols import protocol_image_filter

class DummyImageFilter:
    protocol = protocol_image_filter

    def init(self, context):
        context.log('init()')

    def on_received_image(self, context, data: JPGImage):
        transformed = data
        context.write('image', transformed)

    def finish(self, context):
        context.log('finish()')
