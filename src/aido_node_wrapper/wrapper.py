import argparse
import inspect
import json
import os
import select
import socket
import stat
import sys
import time
from typing import List, Optional, Iterator, Dict, Tuple

from networkx.drawing.nx_pydot import write_dot

from aido_node_wrapper.constants import TOPIC_SET_CONFIG
from aido_nodes import InteractionProtocol, InputReceived, OutputProduced, Unexpected, LanguageChecker, logger
from aido_nodes.structures import TimingInfo, local_time, TimeSpec, timestamp_from_seconds
from compmake.utils import import_name
from contracts import check_isinstance
from contracts.utils import format_obs
from zuper_json.ipce import object_to_ipce, ipce_to_object


def aido_node_wrap_main():
    prog = 'aido_node_wrap'
    usage = ''
    parser = argparse.ArgumentParser(prog=prog, usage=usage)
    parser.add_argument('--implementation', required=True)
    parser.add_argument('--protocol', required=True)
    parsed, remaining = parser.parse_known_args()
    kn = parsed.implementation
    pn = parsed.protocol

    sys.path.insert(0, os.getcwd())

    protocol = import_name(pn)
    logger.info(protocol)
    check_isinstance(protocol, InteractionProtocol)
    k = import_name(kn)
    logger.info(k)
    if isinstance(k, type):
        node = k()
    else:
        node = k
    check_implementation(node, protocol)


def wrap_direct(node, protocol, args: Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        msg = 'Provide one command (run, describe-node, describe-protocol)'
        raise Exception(msg)

    cmd = args.pop(0)
    if cmd == 'run':
        run_loop(node, protocol, args)
    elif cmd == 'describe-node':
        describe_node(node)
    elif cmd == 'describe-protocol':
        describe_protocol(protocol)
    else:
        msg = f'Could not interpret command {cmd}'
        raise Exception(msg)


def describe_node(node):
    from zuper_json.ipce import object_to_ipce
    res = {}
    if hasattr(node, 'config'):
        config_json = object_to_ipce(node.config, globals(), with_schema=False)
        res['config'] = config_json

    print(json.dumps(res, indent=2))


def describe_protocol(protocol):
    from zuper_json.ipce import object_to_ipce
    s = object_to_ipce(protocol, globals(), with_schema=False)
    print(json.dumps(s, indent=2))


class Context:
    protocol: InteractionProtocol

    def __init__(self, of, protocol, pc, node_name, tout: Dict[str, str]):
        self.of = of
        self.protocol = protocol
        self.pc = pc
        self.node_name = node_name
        self.hostname = socket.gethostname()
        self.tout = tout

        self.last_timing = None

    def set_last_timing(self, timing: TimingInfo):
        self.last_timing = timing

    def get_hostname(self):
        return self.hostname

    def write(self, topic, data, timing=None):

        if topic not in self.protocol.outputs:
            msg = f'Output channel "{topic}" not found in protocol; know {sorted(self.protocol.outputs)}.'
            raise Exception(msg)

        event = OutputProduced(topic)
        res = self.pc.push(event)
        if isinstance(res, Unexpected):
            msg = f'Unexpected output {topic}: {res}'
            logger.error(msg)
        else:
            klass = self.protocol.outputs[topic]

            if isinstance(data, dict):
                data = ipce_to_object(data, {}, {}, expect_type=klass)

            if timing is None:
                timing = self.last_timing

            s = time.time()
            hostname = socket.gethostname()
            if timing.received is None:
                # XXX
                time1 = timestamp_from_seconds(s)
            else:
                time1 = timing.received.time
            processed = TimeSpec(time=time1,
                                 time2=timestamp_from_seconds(s),
                                 frame='epoch',
                                 clock=hostname)
            timing.processed[self.node_name] = processed
            # timing = TimingInfo(acquired=acquired, processed=processed)
            m = {}
            m['topic'] = self.tout.get(topic, topic)
            m['data'] = object_to_ipce(data, {}, with_schema=False)
            timing.received = None
            m['timing'] = object_to_ipce(timing, {}, with_schema=False)

            j = json.dumps(m)
            self.of.write(j)
            self.of.write('\n')
            self.of.flush()

    def log(self, s):
        prefix = f'{self.hostname}:{self.node_name}: '
        logger.info(prefix + s)


def get_translation_table(t: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    tout = {}
    tin = {}
    for t in t.split(','):
        ts = t.split(':')
        if ts[0] == 'in':
            tin[ts[1]] = ts[2]

        if ts[0] == 'out':
            tout[ts[1]] = ts[2]

    return tin, tout


def run_loop(node, protocol: InteractionProtocol, args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='/dev/stdin')
    parser.add_argument('--output', default='/dev/stdout')
    parser.add_argument('--name', default=None)

    parser.add_argument('--translate', default='')
    parser.add_argument('--loose', default=False, action='store_true')

    parsed = parser.parse_args(args)

    tin, tout = get_translation_table(parsed.translate)

    # expect in:name1:name2, out:name2:name1

    fin = parsed.input
    fout = parsed.output

    # if not os.path.exists(fout):
    #     os.mkfifo(fout)

    if parsed.output == '/dev/stdout':
        fo = sys.stdout
    else:
        logger.info(f'Opening output file {fout}')

        if os.path.exists(fout):
            is_fifo = stat.S_ISFIFO(os.stat(fout).st_mode)
            if is_fifo:
                logger.info('Fifo detected. This will block until a reader appears.')

        fo = open(fout, 'w')

    while not os.path.exists(fin):
        logger.info(f'waiting for file {fin} to be created')
        time.sleep(1)

    node_name = parsed.name or type(node).__name__

    try:
        with open(fin) as fi:
            loop(node_name, fi, fo, node, protocol, tin, tout)
    except BaseException as e:
        logger.error(f'Error in node {node_name}: \n{e}')
        raise


def loop(node_name, fi, fo, node, protocol, tin, tout):
    logger.info(f'Starting reading')

    pc = LanguageChecker(protocol.interaction)
    fn = 'language.dot'
    write_dot(pc.g, fn)
    logger.info(f'Wrote graph to {fn}')

    context = Context(of=fo, protocol=protocol, pc=pc, node_name=node_name, tout=tout)
    call_if_fun_exists(node, 'init', context=context)

    for parsed in inputs(fi):
        topic = parsed['topic']
        topic = tin.get(topic, topic)
        logger.info(f'received {topic}')
        if topic.startswith('wrapper.'):
            parsed['topic'] = topic.replace('wrapper.', '')
            handle_message_wrapper(parsed, node, context)
        else:
            handle_message_node(parsed, protocol, pc, node, context)

    res = pc.finish()
    if isinstance(res, Unexpected):
        msg = f'Protocol did not finish: {res}'
        logger.error(msg)

    call_if_fun_exists(node, 'finish', context=context)


def handle_message_wrapper(parsed, node, context):
    topic = parsed['topic']
    data = parsed['data']

    if topic == TOPIC_SET_CONFIG:
        key = data['key']
        value = data['value']

        if hasattr(node, 'config'):
            config = node.config
            if hasattr(config, key):
                setattr(node.config, key, value)
            else:
                logger.error(f'Could not find config key {key}')

            call_if_fun_exists(node, 'on_updated_config', context=context, key=key, value=value)
        else:
            logger.warning('Node does not have the "config" attribute.')

    else:
        logger.error("unknown topic %s" % topic)


def handle_message_node(parsed, protocol, pc: LanguageChecker, agent, context):
    topic = parsed['topic']
    data = parsed['data']

    if topic not in protocol.inputs:
        msg = f'Input channel "{topic}" not found in protocol. Known: {sorted(protocol.inputs)}'
        raise Exception(msg)

    klass = protocol.inputs[topic]

    ob = ipce_to_object(data, {}, {}, expect_type=klass)
    if 'timing' in parsed:
        timing = ipce_to_object(parsed['timing'], {}, {}, expect_type=TimingInfo)
    else:
        timing = TimingInfo()

    timing.received = local_time()

    context.set_last_timing(timing)
    # logger.info(f'Before push the state is\n{pc}')

    event = InputReceived(topic)
    res = pc.push(event)

    # names = pc.get_active_states_names()
    # logger.info(f'After push of {event}: result \n{res} active {names}' )
    if isinstance(res, Unexpected):
        msg = f'Unexpected input "{topic}": {res}'
        msg += '\n' + format_obs(dict(pc=pc))
        logger.error(msg)
        raise Exception(msg)
    else:
        expect_fn = f'on_received_{topic}'
        call_if_fun_exists(agent, expect_fn, data=ob, context=context, timing=timing)


def inputs(fifo, timeout=1.0) -> Iterator[Dict]:
    while True:
        readyr, readyw, readyx = select.select([fifo], [], [fifo], timeout)
        if readyr:
            # logger.info(f'reading...')
            data = fifo.readline()

            if data == '':
                logger.info(f'EOF')
                break

            data = data.strip()
            if not data:
                continue

            # logger.info(f'read {data!r}')
            parsed = json.loads(data)

            # check fields

            yield parsed
        elif readyx:
            logger.warning('Exceptional condition on input channel.')
        else:
            logger.warning(f'Input channel not ready after {timeout} seconds. Will re-try')


import contracts


def call_if_fun_exists(ob, fname, **kwargs):
    kwargs = dict(kwargs)
    if not hasattr(ob, fname):
        msg = f'Missing function {fname}() for {contracts.describe_type(ob)}'
        logger.warning(msg)
        return
    f = getattr(ob, fname)
    a = inspect.getfullargspec(f)
    for k, v in dict(kwargs).items():
        if k not in a.args:
            kwargs.pop(k)
    f(**kwargs)


class NotConforming(ValueError):
    pass


def check_implementation(node, protocol: InteractionProtocol):
    for n in protocol.inputs:
        expect_fn = f'on_received_{n}'
        if not hasattr(node, expect_fn):
            msg = f'Missing function {expect_fn}'
            msg += f'\nI know {sorted(node.__dict__)}'
            raise NotConforming(msg)
