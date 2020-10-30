#!/usr/bin/env python3

import numpy as np

from aido_schemas import (
    JPGImage,
    Duckiebot1Observations,
    Duckiebot1Commands,
    wrap_direct,
    Context,
    SetMap,
    SpawnRobot,
    RobotName,
    StateDump,
    Step,
    RobotInterfaceDescription,
    RobotState,
    protocol_simulator_duckiebot1,
    RobotPerformance,
    Metric,
    PerformanceMetrics,
    DB18SetRobotCommands,
    DB18RobotObservations,
)


class DummySimulator:
    """ A dummy simulator implementation. """

    current_time: float
    robot_name: str

    def init(self, context: Context):
        context.info("init()")

    def on_received_seed(self, context: Context, data: int):
        context.info(f"seed({data})")

    def on_received_clear(self, context: Context):
        context.info(f"clear()")

    def on_received_set_map(self, context: Context, data: SetMap):
        context.info(f"set_map({data})")
        # TODO: load map

    def on_received_spawn_robot(self, data: SpawnRobot):
        self.robot_name = data.robot_name
        # TODO: set pose of robot

    def on_received_get_robot_interface_description(self, context: Context, data: RobotName):
        rid = RobotInterfaceDescription(
            robot_name=data, observations=Duckiebot1Observations, commands=Duckiebot1Commands
        )
        context.write("robot_interface_description", rid)

    def on_received_get_robot_performance(self, context: Context, data: RobotName):
        context.info(f"get_robot_interface_description()")
        metrics = {}
        metrics["reward"] = Metric(
            higher_is_better=True,
            cumulative_value=self.current_time,
            description="Dummy reward equal to survival time.",
        )
        pm = PerformanceMetrics(metrics)
        rid = RobotPerformance(robot_name=data, t_effective=self.current_time, performance=pm)
        context.write("robot_performance", rid)

    def on_received_episode_start(self, context: Context):
        context.info(f"episode_start()")
        self.current_time = 0

    def on_received_step(self, context: Context, data: Step):
        context.info(f"step({data})")
        self.current_time = data.until

    def on_received_set_robot_commands(self, context: Context, data: DB18SetRobotCommands):
        context.info(f"set_robot_commands({data})")

    def on_received_get_robot_observations(self, context, data: RobotName):
        context.log(f"get_robot_observation({data!r})")
        camera = get_random_image(shape=(200, 300))
        obs = Duckiebot1Observations(camera)
        ro = DB18RobotObservations(
            robot_name=self.robot_name, t_effective=self.current_time, observations=obs
        )
        context.write("robot_observations", ro, with_schema=True)

    def on_received_get_robot_state(self, context: Context, data: RobotName):
        context.info(f"get_robot_state({data!r})")
        rs = RobotState(robot_name=data, t_effective=self.current_time, state=None)
        context.write("robot_state", rs)

    def on_received_dump_state(self, context: Context):
        context.info(f"dump_state()")
        context.write("dump_state", StateDump(None))


def get_random_image(shape):
    H, W = shape
    values = (128 + np.random.randn(H, W, 3) * 60).astype("uint8")
    jpg_data = bgr2jpg(values)
    image = JPGImage(jpg_data)
    return image


import cv2

# noinspection PyUnresolvedReferences
def bgr2jpg(image_cv) -> bytes:
    compress = cv2.imencode(".jpg", image_cv)[1]
    jpg_data = np.array(compress).tostring()
    return jpg_data


def main():
    node = DummySimulator()
    protocol = protocol_simulator_duckiebot1
    wrap_direct(node=node, protocol=protocol)


if __name__ == "__main__":
    main()
