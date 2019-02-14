from aido_nodes import Context


class DummyFilter:

    def init(self):
        pass

    def on_received_image(self, context: Context, data):
        context.write('image', data)

    def finish(self):
        pass
