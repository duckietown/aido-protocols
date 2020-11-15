__version__ = "6.0.29"

from zuper_commons.logs import ZLogger

logger = ZLogger(__name__)
logger.debug(f"aido-protocols version {__version__} path {__file__}")

from .protocols import *
from .protocol_agent import *
from .protocol_simulator import *
from .schemas import *
from .basics import *
