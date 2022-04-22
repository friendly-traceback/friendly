"""Sets up everything required for an IPython terminal session."""
from friendly.ipython_common import excepthook
from friendly.ipython_common.settings import init_settings

from friendly import print_repl_header
from friendly import settings
from friendly_traceback import config
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import __all__  # noqa

import colorama

colorama.deinit()  # Required to get correct colours in Windows terminal
colorama.init(convert=False, strip=False)

if settings.terminal_type:
    settings.ENVIRONMENT = settings.terminal_type + "-ipython"
else:
    settings.ENVIRONMENT = "ipython"

excepthook.enable()
init_settings("dark")
print_repl_header()
if config.did_exception_occur_before():
    friendly_tb()  # noqa
