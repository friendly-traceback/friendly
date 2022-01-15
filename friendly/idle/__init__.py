import friendly
from .main import *  # noqa
from .main import install
from friendly import settings
from friendly_traceback.console_helpers import friendly_tb
from friendly_traceback import config

settings.ENVIRONMENT = "IDLE"

__all__ = list(helpers)  # noqa
__all__.append("run")  # noqa
__all__.append("start_console")  # noqa
__all__.append("Friendly")  # noqa
install()

if config.did_exception_occur_before():
    friendly.print_repl_header()
    friendly_tb()  # noqa
