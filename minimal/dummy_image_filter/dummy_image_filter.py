
class DummyFilter:

    def init(self):
        pass

    def on_received_image(self, context, image):
        context.publish('image', image)

    def shutdown(self):
        pass
