import sys

from aido_schemas.utils_drawing import read_simulator_log_cbor
from procgraph import Generator, Block, register_model_spec, pg


class CBORRead(Generator):
    '''
    '''
    Block.alias('cborread')
    Block.output('image')
    Block.config('filename', 'CBOR file to read')
    Block.config('robot_name', 'robot name', default='ego')

    def init(self):
        self.log = read_simulator_log_cbor(self.get_config('filename'))
        self.i = 0
        log = self.log.robots[self.config.robot_name]
        self.n = len(log.observations)

    def next_data_status(self):
        log = self.log.robots[self.config.robot_name]
        if self.i < self.n:
            return True, log.observations.timestamps[self.i]
        else:
            return False, None

    def update(self):
        i = self.i
        log = self.log.robots[self.config.robot_name]
        timestamp = log.observations.timestamps[i]
        value = log.observations.values[i]
        self.set_output('image', value=value, timestamp=timestamp)

        self.i += 1

    def finish(self):
        pass


def make_video1(fn, output):
    register_model_spec("""
    --- model video_aido
    config output
    config filename
    

    |cborread filename=$filename| --> |jpg2rgb| -> rgb
    rgb -> |identity| -> retimed
    # rgb --> |rewrite_timestamps interval=$factor| -> retimed
    retimed --> |info|
    retimed -> |mencoder quiet=1 file=$output timestamps=0|

        """)

    pg('video_aido', dict(filename=fn, output=output))


def aido_log_video_main():
    make_video1(sys.argv[1], 'out-aido-log-video.mp4')


if __name__ == '__main__':
    make_video1(sys.argv[1], 'out-aido-log-video.mp4')
