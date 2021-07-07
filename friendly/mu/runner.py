"""Mu's runner launches a Python interpreter and feeds back the result
into a console that does not support colour.

If we try to "install" friendly-traceback in that console, SyntaxErrors
are properly captured but any runtime error simply disappear.

For this reason, we only provide two basic ways to start friendly-traceback
in this situation.
"""

from ..my_gettext import current_lang  # noqa

from friendly_traceback.runtime_errors import name_error
from friendly_traceback import run, start_console  # noqa


def _cause():
    _ = current_lang.translate
    return _("Friendly themes are only available in Mu's REPL.\n")


for name in ("bw", "day", "night"):
    name_error.CUSTOM_NAMES[name] = _cause

__all__ = ["run", "start_console"]
