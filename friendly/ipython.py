"""Experimental module to automatically install Friendly
as a replacement for the standard traceback in IPython."""

try:
    from IPython.core import interactiveshell as shell  # noqa
    from IPython.core import compilerop  # noqa
except ImportError:
    raise ValueError("IPython cannot be imported.")

import colorama

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
    session,  # noqa
)  # noqa
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import FriendlyHelpers, helpers  # noqa

try:
    from IPython.utils import py3compat  # noqa

    exclude_file_from_traceback(py3compat.__file__)
except Exception:  # noqa
    pass


colorama.deinit()
colorama.init(convert=False, strip=False)


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using Rich."""
    if session.use_rich:
        session.console._width = width
    else:
        print("set_width() is only available using 'light' or 'dark' mode.")


set_width.help = lambda: "Sets the output width in 'light' or 'dark' mode."
setattr(set_width, "__rich_repr__", lambda: (set_width.help(),))
FriendlyHelpers.set_width = set_width
Friendly = FriendlyHelpers(
    local_helpers={"set_width": set_width, "light": light, "dark": dark}  # noqa
)

shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)
exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)
install(include="friendly_tb")

set_formatter("dark")  # noqa
helpers["Friendly"] = Friendly
helpers["set_width"] = set_width
__all__ = list(helpers.keys())
