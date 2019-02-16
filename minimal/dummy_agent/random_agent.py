import numpy as np

from aido_nodes import PWMCommands


class RandomAgent:

    def init(self, context):
        context.log('init()')

    def on_received_image(self, context, data):
        pwm_left  = np.random.uniform(0.0, 1.0)
        pwm_right = np.random.uniform(0.0, 1.0)

        commands = PWMCommands(motor_left=pwm_left, motor_right=pwm_right)
        context.write('commands', commands)

    def finish(self, context):
        context.log('finish()')
