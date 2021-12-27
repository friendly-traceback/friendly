"""Sets up everything required for an IPython terminal session."""
from friendly import ipython_excepthook  # noqa
from friendly import ipython_configuration

from friendly import print_repl_header
from friendly import configuration
from friendly_traceback import config
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import __all__  # noqa

if configuration.terminal_type:
    configuration.ENVIRONMENT = configuration.terminal_type + "-ipython"
else:
    configuration.ENVIRONMENT = "ipython"
ipython_configuration.init_configuration("dark")
if config.did_exception_occur_before():
    friendly_tb()  # noqa

print_repl_header()
