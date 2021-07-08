"""Mu's runner launches a Python interpreter and feeds back the result
into a console that does not support colour.
"""
import sys  # noqa
from ..my_gettext import current_lang  # noqa

from friendly_traceback.runtime_errors import name_error
from friendly_traceback import run, start_console, install  # noqa

from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import __all__


def _cause():
    _ = current_lang.translate
    return _("Friendly themes are only available in Mu's REPL.\n")


for name in ("bw", "day", "night", "black"):
    name_error.CUSTOM_NAMES[name] = _cause

__all__.append("run")
__all__.append("start_console")
install(redirect=sys.stderr.write, include="friendly_tb")
