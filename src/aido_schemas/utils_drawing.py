import sys
from collections import OrderedDict
from dataclasses import dataclass

import yaml

from . import logger
from aido_schemas import RobotState, RobotObservations, Duckiebot1Observations, SetRobotCommands
from duckietown_world import SE2Transform, SampledSequence, DuckietownMap, draw_static
from duckietown_world.rules import evaluate_rules
from duckietown_world.rules.rule import make_timeseries
from duckietown_world.seqs.tsequence import SampledSequenceBuilder
from duckietown_world.svg_drawing.draw_log import SimulatorLog, timeseries_actions
from duckietown_world.svg_drawing.misc import TimeseriesPlot
from zuper_json import read_cbor_or_json_objects
from zuper_json.ipce import ipce_to_object


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


@dataclass
class Trajectories:
    pose: SampledSequence
    wheels_velocities: SampledSequence
    actions: SampledSequence
    velocity: SampledSequence


def read_trajectories(filename) -> Trajectories:
    rs = list(read_topic(filename, 'robot_state'))
    if not rs:
        msg = 'Could not find robot_state'
        raise Exception(msg)

    ssb_pose = SampledSequenceBuilder()
    ssb_actions = SampledSequenceBuilder()
    ssb_wheels_velocities = SampledSequenceBuilder()
    ssb_velocities = SampledSequenceBuilder()
    for r in rs:
        robot_state: RobotState = ipce_to_object(r['data'], {}, {})

        pose = robot_state.state.pose
        velocity = robot_state.state.velocity
        last_action = robot_state.state.last_action
        wheels_velocities = robot_state.state.wheels_velocities

        t = robot_state.t_effective
        ssb_pose.add(t, SE2Transform.from_SE2(pose))
        ssb_actions.add(t, last_action)
        ssb_wheels_velocities.add(t, wheels_velocities)
        ssb_velocities.add(t, velocity)

    return Trajectories(ssb_pose.as_sequence(),
                        ssb_actions.as_sequence(),
                        ssb_wheels_velocities.as_sequence(),
                        ssb_velocities.as_sequence())


from duckietown_world.world_duckietown import DB18, construct_map


def read_observations(filename):
    ssb = SampledSequenceBuilder()
    obs = list(read_topic(filename, 'robot_observations'))
    for ob in obs:
        ro: RobotObservations = ipce_to_object(ob['data'], {}, {})
        do: Duckiebot1Observations = ro.observations
        t = ro.t_effective
        camera = do.camera.jpg_data
        ssb.add(t, camera)
    return ssb.as_sequence()


def read_commands(filename):
    ssb = SampledSequenceBuilder()
    obs = list(read_topic(filename, 'set_robot_commands'))
    for ob in obs:
        ro: SetRobotCommands = ipce_to_object(ob['data'], {}, {})
        ssb.add(ro.t_effective, ro.commands)
    seq = ssb.as_sequence()
    if len(seq) == 0:
        msg = 'Could not find any robot_commands in the log'
        logger.warning(msg)
    return seq


def read_simulator_log_cbor(filename) -> SimulatorLog:
    duckietown_map = read_map_info(filename)
    trajectories = read_trajectories(filename)
    observations = read_observations(filename)
    commands = read_commands(filename)

    robot = DB18()
    duckietown_map.set_object('ego',
                              robot,
                              ground_truth=trajectories.pose)
    #
    # render_time = builders[TOPIC_RENDER_TIME].as_sequence()
    # actions = builders[TOPIC_ACTIONS].as_sequence()
    #
    actions = trajectories.actions
    render_time = None

    return SimulatorLog(duckietown=duckietown_map,
                        observations=observations,
                        trajectory=trajectories.pose,
                        render_time=render_time,
                        actions=actions,
                        commands=commands,
                        velocities=trajectories.velocity)


def read_and_draw(fn, output):
    log = read_simulator_log_cbor(fn)
    if log.observations:
        images = {'observations': log.observations}
    else:
        images = None
    duckietown_env = log.duckietown
    timeseries = OrderedDict()

    timeseries.update(timeseries_actions(log))
    timeseries.update(timeseries_wheels_velocities(log.commands))
    timeseries.update(timeseries_robot_velocity(log.velocities))
    interval = SampledSequence.from_iterator(enumerate(log.trajectory.timestamps))
    evaluated = evaluate_rules(poses_sequence=log.trajectory,
                               interval=interval,
                               world=duckietown_env,
                               ego_name='ego')
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
