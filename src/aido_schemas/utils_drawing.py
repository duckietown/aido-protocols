import sys
from collections import OrderedDict
from typing import Dict

import yaml

from aido_schemas import RobotState, RobotObservations, Duckiebot1Observations, SetRobotCommands
from duckietown_world import SE2Transform, SampledSequence, DuckietownMap, draw_static
from duckietown_world.rules import evaluate_rules
from duckietown_world.rules.rule import make_timeseries
from duckietown_world.seqs.tsequence import SampledSequenceBuilder
from duckietown_world.svg_drawing.draw_log import SimulatorLog, timeseries_actions, RobotTrajectories
from duckietown_world.svg_drawing.misc import TimeseriesPlot
from zuper_json import read_cbor_or_json_objects
from zuper_json.ipce import ipce_to_object
from . import logger


def read_topic(filename, topic):
    f = open(filename, 'rb')
    for ob in read_cbor_or_json_objects(f):
        if ob['topic'] == topic:
            yield ob


def read_map_info(filename) -> DuckietownMap:
    m = list(read_topic(filename, 'set_map'))
    if not m:
        msg = 'Could not find set_map'
        raise Exception(msg)
    m = m[0]
    map_data_yaml = m['data']['map_data']
    map_data = yaml.load(map_data_yaml, Loader=yaml.SafeLoader)
    duckietown_map = construct_map(map_data)
    return duckietown_map


def read_trajectories(filename) -> Dict[str, RobotTrajectories]:
    rs = list(read_topic(filename, 'robot_state'))
    if not rs:
        msg = 'Could not find robot_state'
        raise Exception(msg)
    robot_names = set([r['data']['robot_name'] for r in rs])
    logger.info(f'robot_names: {robot_names}')

    robot2trajs = {}
    for robot_name in robot_names:
        ssb_pose = SampledSequenceBuilder()
        ssb_actions = SampledSequenceBuilder()
        ssb_wheels_velocities = SampledSequenceBuilder()
        ssb_velocities = SampledSequenceBuilder()
        for r in rs:

            robot_state: RobotState = ipce_to_object(r['data'], {}, {})
            if robot_state.robot_name != robot_name:
                continue

            pose = robot_state.state.pose
            velocity = robot_state.state.velocity
            last_action = robot_state.state.last_action
            wheels_velocities = robot_state.state.wheels_velocities

            t = robot_state.t_effective
            ssb_pose.add(t, SE2Transform.from_SE2(pose))
            ssb_actions.add(t, last_action)
            ssb_wheels_velocities.add(t, wheels_velocities)
            ssb_velocities.add(t, velocity)

        observations = read_observations(filename, robot_name)
        commands = read_commands(filename, robot_name)

        robot2trajs[robot_name] = RobotTrajectories(ssb_pose.as_sequence(),
                                                    ssb_actions.as_sequence(),
                                                    ssb_wheels_velocities.as_sequence(),
                                                    ssb_velocities.as_sequence(),
                                                    observations=observations,
                                                    commands=commands)
    return robot2trajs


from duckietown_world.world_duckietown import DB18, construct_map


def read_observations(filename, robot_name):
    ssb = SampledSequenceBuilder()
    obs = list(read_topic(filename, 'robot_observations'))
    last_t = None
    for ob in obs:
        ro: RobotObservations = ipce_to_object(ob['data'], {}, {})
        if ro.robot_name != robot_name:
            continue
        do: Duckiebot1Observations = ro.observations

        t = ro.t_effective
        camera = do.camera.jpg_data

        if last_t != t:
            ssb.add(t, camera)
        last_t = t
    return ssb.as_sequence()


def read_commands(filename, robot_name):
    ssb = SampledSequenceBuilder()
    obs = list(read_topic(filename, 'set_robot_commands'))
    last_t = None
    for ob in obs:
        ro: SetRobotCommands = ipce_to_object(ob['data'], {}, {})
        if ro.robot_name != robot_name:
            continue
        t = ro.t_effective
        if last_t != t:
            ssb.add(ro.t_effective, ro.commands)
        last_t = t
    seq = ssb.as_sequence()
    if len(seq) == 0:
        msg = f'Could not find any robot_commands in the log for robot "{robot_name}".'
        logger.warning(msg)
    return seq


def read_simulator_log_cbor(filename) -> SimulatorLog:
    duckietown_map = read_map_info(filename)
    robots = read_trajectories(filename)

    for robot_name, trajs in robots.items():
        robot = DB18()
        duckietown_map.set_object(robot_name,
                                  robot,
                                  ground_truth=trajs.pose)

    render_time = None

    return SimulatorLog(duckietown=duckietown_map,
                        robots=robots,
                        render_time=render_time)


def read_and_draw(fn, output):
    log0 = read_simulator_log_cbor(fn)

    robot_main = 'ego'
    if not robot_main in log0.robots:
        msg = f'Cannot find robot {robot_main}'
        raise Exception(msg)
    log = log0.robots[robot_main]

    if log.observations:
        images = {'observations': log.observations}
    else:
        images = None
    duckietown_env = log0.duckietown
    timeseries = OrderedDict()

    timeseries.update(timeseries_actions(log))
    timeseries.update(timeseries_wheels_velocities(log.commands))
    timeseries.update(timeseries_robot_velocity(log.velocity))
    interval = SampledSequence.from_iterator(enumerate(log.pose.timestamps))
    evaluated = evaluate_rules(poses_sequence=log.pose,
                               interval=interval,
                               world=duckietown_env,
                               ego_name=robot_main)
    timeseries.update(make_timeseries(evaluated))
    draw_static(duckietown_env, output, images=images, timeseries=timeseries)
    return evaluated


def timeseries_wheels_velocities(log_commands):
    timeseries = OrderedDict()
    sequences = OrderedDict()
    sequences['motor_left'] = log_commands.transform_values(lambda _: _.wheels.motor_left)
    sequences['motor_right'] = log_commands.transform_values(lambda _: _.wheels.motor_right)
    timeseries['pwm_commands'] = TimeseriesPlot('PWM commands', 'pwm_commands', sequences)
    return timeseries


import geometry


def timeseries_robot_velocity(log_velocitiy):
    timeseries = OrderedDict()
    sequences = OrderedDict()

    def speed(x):
        l, omega = geometry.linear_angular_from_se2(x)
        return l

    def omega(x):
        l, omega = geometry.linear_angular_from_se2(x)
        return omega

    sequences['linear_speed'] = log_velocitiy.transform_values(lambda _: speed(_))
    sequences['angular_velocity'] = log_velocitiy.transform_values(lambda _: omega(_))
    timeseries['velocity'] = TimeseriesPlot('Velocities', 'velocities', sequences)
    return timeseries


def aido_log_draw_main():
    read_and_draw(sys.argv[1], 'test')


if __name__ == '__main__':
    read_and_draw(sys.argv[1], 'test')
