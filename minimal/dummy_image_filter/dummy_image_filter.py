
class DummyFilter:

    def init(self, context):
        context.log('init()')
        pass

    def on_received_image(self, context, data):
        context.write('image', data)

    def finish(self, context):
        context.log('finish()')
