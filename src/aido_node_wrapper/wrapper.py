import argparse
import inspect
import json

import os
import select
import stat
import sys
import time
from typing import List, Optional

from aido_nodes import InteractionProtocol, InputReceived, OutputProduced
from aido_nodes_tests.test_protocol import Unexpected, LanguageChecker
from compmake.utils import import_name
from contracts import check_isinstance
from contracts.utils import format_obs

from aido_nodes import logger


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
        agent = k()
    else:
        agent = k
    check_implementation(agent, protocol)


def wrap_direct(agent, protocol, args: Optional[List[str]] = None):
    if args is None:
        args = sys.argv[1:]
    if not args:
        msg = 'Provide one command (run, describe-agent, describe-protocol)'
        raise Exception(msg)

    cmd = args.pop(0)
    if cmd == 'run':
        run_loop(agent, protocol, args)
    elif cmd == 'describe-agent':
        describe_agent(agent)
    elif cmd == 'describe-protocol':
        describe_protocol(protocol)
    else:
        msg = f'Could not interpret command {cmd}'
        raise Exception(msg)


def describe_agent(agent):
    from zuper_json.ipce import object_to_ipce
    res = {}
    if hasattr(agent, 'config'):
        config_json = object_to_ipce(agent.config, globals(), with_schema=False)
        res['config'] = config_json

    print(json.dumps(res, indent=2))


def describe_protocol(protocol):
    from zuper_json.ipce import object_to_ipce
    s = object_to_ipce(protocol, globals(), with_schema=False)
    print(json.dumps(s, indent=2))


class Context:
    protocol: InteractionProtocol

    def __init__(self, of, protocol, pc):
        self.of = of
        self.protocol = protocol
        self.pc = pc

    def write(self, topic, data):
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

            from zuper_json.ipce import ipce_to_object, object_to_ipce

            if isinstance(data, dict):
                ob = ipce_to_object(data, {}, {}, expect_type=klass)
            else:
                ob = data
            data = object_to_ipce(ob, {}, with_schema=False)
            m = {'topic': topic, 'data': data}
            j = json.dumps(m)
            self.of.write(j)
            self.of.write('\n')
            self.of.flush()

    def log(self, s):
        logger.info(s)


def run_loop(agent, protocol: InteractionProtocol, args: Optional[List[str]] = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='/dev/stdin')
    parser.add_argument('--output', default='/dev/stdout')
    parser.add_argument('--loose', default=False, action='store_true')

    parsed = parser.parse_args(args)

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

    logger.info(f'Starting reading')

    pc = LanguageChecker(protocol.interaction)
    context = Context(of=fo, protocol=protocol, pc=pc)
    call_if_fun_exists(agent, 'init', context=context)

    with open(fin) as fifo:
        for parsed in inputs(fifo):

            topic: str = parsed['topic']
            data = parsed['data']

            if topic.startswith('wrapper.'):
                topic = topic.replace('wrapper.', '')

                if topic == 'set_config':
                    key = data['key']
                    value = data['value']

                    if hasattr(agent, 'config'):
                        config = agent.config
                        if hasattr(config, key):
                            setattr(agent.config, key, value)
                        else:
                            logger.error(f'Could not find config key {key}')
                    call_if_fun_exists(agent, 'on_updated_config', context=context, key=key, value=value)
                    continue

            else:

                if topic not in protocol.inputs:
                    msg = f'Input channel "{topic}" not found in protocol. Known: {sorted(protocol.inputs)}'
                    raise Exception(msg)

                klass = protocol.inputs[topic]
                from zuper_json.ipce import ipce_to_object

                ob = ipce_to_object(data, {}, {}, expect_type=klass)

                # logger.info(f'Before push the state is\n{pc}')

                event = InputReceived(topic)
                res = pc.push(event)
                # logger.info(f'After push of {event} the state is\n{pc}' )
                if isinstance(res, Unexpected):
                    msg = f'Unexpected input "{topic}": {res}'
                    msg += '\n' + format_obs(dict(pc=pc))
                    logger.error(msg)
                    raise Exception(msg)
                else:
                    expect_fn = f'on_received_{topic}'
                    call_if_fun_exists(agent, expect_fn, data=ob, context=context)
                #
                # if hasattr(agent, expect_fn):
                #     f = getattr(agent, expect_fn)
                #
                #     f(data=data, context=context)
                # else:
                #     msg = f'Missing function {expect_fn}'
                #     msg += f'\nI know {sorted(agent.__dict__)}'
                #     raise NotConforming(msg)

    res = pc.finish()
    if isinstance(res, Unexpected):
        msg = f'Protocol did not finish: {res}'
        logger.error(msg)

    call_if_fun_exists(agent, 'finish', context=context)


def inputs(fifo):
    while True:
        timeout = 1.0
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
            yield parsed
        elif readyx:
            logger.info('ex')
        else:
            logger.info('Input channel not ready.')


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


def check_implementation(agent, protocol: InteractionProtocol):
    for n in protocol.inputs:
        expect_fn = f'on_received_{n}'
        if not hasattr(agent, expect_fn):
            msg = f'Missing function {expect_fn}'
            msg += f'\nI know {sorted(agent.__dict__)}'
            raise NotConforming(msg)
