"""Sets up everything required for an IPython terminal session."""
from friendly.ipython_common.excepthook import install_except_hook
from friendly.ipython_common.settings import init_configuration

from friendly import print_repl_header
from friendly import configuration
from friendly_traceback import config
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import __all__  # noqa

import colorama

colorama.deinit()  # Required to get correct colours in Windows terminal
colorama.init(convert=False, strip=False)

if configuration.terminal_type:
    configuration.ENVIRONMENT = configuration.terminal_type + "-ipython"
else:
    configuration.ENVIRONMENT = "ipython"

install_except_hook()
init_configuration("dark")
print_repl_header()
if config.did_exception_occur_before():
    friendly_tb()  # noqa
