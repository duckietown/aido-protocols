__version__ = "5.0.20"


import logging

logging.basicConfig()
logger = logging.getLogger("aido-protocols")
logger.setLevel(logging.DEBUG)
logger.info(f"aido-protocols {__version__}")

from zuper_nodes import InteractionProtocol, particularize

from zuper_nodes_wrapper import wrap_direct, Context

_ = wrap_direct
_ = Context
_ = InteractionProtocol
_ = particularize

from .protocol_agent import *
from .protocol_simulator import *
from .protocols import *
from .schemas import *
