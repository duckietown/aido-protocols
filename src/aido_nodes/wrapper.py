import argparse
import inspect
import json
import logging
import os
import select
import sys
import time
from typing import List

from aido_nodes import InteractionProtocol
from compmake.utils import import_name
from contracts import check_isinstance

logging.basicConfig()
logger = logging.getLogger('reader')
logger.setLevel(logging.DEBUG)
sys.stderr.flush()


def aido_node_wrap_main():
    print('OK')

    prog = 'aido_node_wrap'
    usage = ''
    parser = argparse.ArgumentParser(prog=prog, usage=usage)
    parser.add_argument('--implementation', required=True)
    parser.add_argument('--protocol', required=True)
    # group.add_argument('--user-label', dest='message', default=None, type=str,
    #                    help="Submission message")
    # group.add_argument('--user-meta', dest='metadata', default=None, type=str,
    #                    help="Custom JSON structure to attach to the submission")
    #
    # group = parser.add_argument_group("Building settings.")
    # group.add_argument('--image', default=None, type=str,
    #                    help="Specify image directly instead of building it.")
    # group.add_argument('--no-push', dest='no_push', action='store_true', default=False,
    #                    help="Disable pushing of container")
    # group.add_argument('--no-submit', dest='no_submit', action='store_true', default=False,
    #                    help="Disable submission (only build and push)")
    # group.add_argument('--no-cache', dest='no_cache', action='store_true', default=False)
    # group.add_argument('--impersonate', type=int, default=None)
    #
    # group.add_argument('-C', dest='cwd', default=None, help='Base directory')

    parsed, remaining = parser.parse_known_args()
    kn = parsed.implementation
    pn = parsed.protocol

    sys.path.insert(0, os.getcwd())

    protocol = import_name(pn)
    print(protocol)
    check_isinstance(protocol, InteractionProtocol)
    k = import_name(kn)
    print(k)
    if isinstance(k, type):
        agent = k()
    else:
        agent = k
    check_implementation(agent, protocol)

    if not remaining:
        msg = 'Provide one command (run, describe-agent, describe-protocol)'
        raise Exception(msg)

    cmd = remaining.pop(0)
    if cmd == 'run':
        run_loop(agent, protocol, remaining)
    elif cmd == 'describe-agent':
        describe_agent(agent)
    elif cmd == 'describe-protocol':
        describe_protocol(agent)
    else:
        msg = f'Could not interpret command {cmd}'
        raise Exception(msg)


def describe_agent(agent):
    pass


def describe_protocol(protocol):
    pass


class Context:
    def __init__(self, of):
        self.of = of

    def write(self, topic, data):
        m = {'topic': topic, 'data': data}
        j = json.dumps(m)
        self.of.write(j)
        self.of.write('\n')
        self.of.flush()


def run_loop(agent, protocol, args: List[str]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', default='/dev/stdin')
    parser.add_argument('--output', default='/dev/stdout')
    parser.add_argument('--config', default='/dev/stdin')
    parser.add_argument('--extra', default='/dev/stdout')

    parsed = parser.parse_args(args)
    print(parsed)

    fin = parsed.input
    fout = parsed.output

    if not os.path.exists(fout):
        os.mkfifo(fout)

    fo = open(fout, 'a')

    while not os.path.exists(fin):
        logger.info(f'waiting for file {fin} to be created')
        time.sleep(1)



    context = Context(fo)
    call_if_fun_exists(agent, 'init', context)
    with open(fin) as fifo:
        while True:
            timeout = 1.0
            readyr, readyw, readyx = select.select([fifo], [], [fifo], timeout)
            if readyr:
                logger.info(f'reading...')
                data = fifo.readline()

                if data == '':
                    logger.info(f'EOF')
                    call_if_fun_exists(agent, 'finish', context)
                    break

                data = data.strip()
                if not data:
                    continue

                logger.info(f'read {data!r}')
                parsed = json.loads(data)

                topic = parsed['topic']
                data = parsed['data']
                expect_fn = f'on_received_{topic}'
                if hasattr(agent, expect_fn):
                    f = getattr(agent, expect_fn)

                    f(data=data, context=context)
                else:
                    msg = f'Missing function {expect_fn}'
                    msg += f'\nI know {sorted(agent.__dict__)}'
                    raise NotConforming(msg)


            elif readyx:
                logger.info('ex')
            else:
                logger.info('Input channel not ready.')

import contracts

def call_if_fun_exists(ob, fname, context):
    if not hasattr(ob, fname):
        msg = f'Missing function {fname}() for {contracts.describe_type(ob)}'
        logger.warning(msg)
        return
    f = getattr(ob, fname)
    a = inspect.getfullargspec(f)
    if 'context' in a.args:
        f(context=context)
    else:
        f()


class NotConforming(ValueError):
    pass


def check_implementation(agent, protocol: InteractionProtocol):
    for n in protocol.inputs:
        expect_fn = f'on_received_{n}'
        if not hasattr(agent, expect_fn):
            msg = f'Missing function {expect_fn}'
            msg += f'\nI know {sorted(agent.__dict__)}'
            raise NotConforming(msg)
