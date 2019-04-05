__version__ = '4.0.5'

from zuper_nodes import InteractionProtocol, particularize, logger as zlogger

logger = zlogger.getChild('aido_schemas')
logger.info(f'aido_schemas {__version__}')

from zuper_nodes_wrapper import wrap_direct, Context

_ = wrap_direct
_ = Context
_ = InteractionProtocol
_ = particularize

from .protocol_agent import *
from .protocol_simulator import *
from .protocols import *
from .schemas import *
