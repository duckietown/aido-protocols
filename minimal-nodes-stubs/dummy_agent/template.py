#!/usr/bin/env python3
import numpy as np

from aido_nodes import PWMCommands, protocol_agent_jpg_pwm, wrap_direct


class FakeEnvironment(Environment):

    def on_received_camera_image(self, context, data):
        rgb = ...
        slef.observations.push(rgb)

    def step(self, commands):
        # get the last observation received
        last = self.observations[-1]
        pwm = gym2pwm()
        context.write('pwm_commands', pwm)
        return last

def main():
    import sys
    agent = RandomAgent()
    protocol = protocol_agent_jpg_pwm

    thread1.run(your_agent, my_fake_environment)
    thread2.run(wrap_direct(agent=agent, protocol=protocol, args=sys.argv[1:]))

#
# class WrapsGymAgent:
#
#     def __init__(self, my_gym_agent):
#
#         pass
#
#
#     def on_received_camera_image(self, context, data):
#
#         rgb = ...
#         data['observations'] = ...
#
#         self.my_gym_agent
#
#         pwm_left  = np.random.uniform(0.0, 1.0)
#         pwm_right = np.random.uniform(0.0, 1.0)
#
#         commands = PWMCommands(motor_left=pwm_left, motor_right=pwm_right)
#         context.write('pwm_commands', commands)



if __name__ == '__main__':
    main()
