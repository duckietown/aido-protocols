
class DummyFilter:

    def init(self, context):
        context.log('init()')

    def on_received_image(self, context, data):
        transformed = data
        context.write('image', transformed)

    def finish(self, context):
        context.log('finish()')
