#!/usr/bin/env python3
import numpy as np

from aido_node_wrapper import wrap_direct
from aido_schemas import PWMCommands, protocol_agent_jpg_pwm


class RandomAgent:

    def init(self, context):
        context.log('init()')

    def on_received_camera_image(self, context, data):
        pwm_left = np.random.uniform(0.0, 1.0)
        pwm_right = np.random.uniform(0.0, 1.0)

        commands = PWMCommands(motor_left=pwm_left, motor_right=pwm_right)
        context.write('pwm_commands', commands)

    def finish(self, context):
        context.log('finish()')


def main():
    node = RandomAgent()
    protocol = protocol_agent_jpg_pwm
    wrap_direct(node=node, protocol=protocol)


if __name__ == '__main__':
    main()
