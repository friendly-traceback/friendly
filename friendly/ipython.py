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
    __version__,
)  # noqa
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import FriendlyHelpers, helpers  # noqa
from friendly import __version__ as version

try:
    from IPython.utils import py3compat  # noqa

    exclude_file_from_traceback(py3compat.__file__)
except Exception:  # noqa
    pass


colorama.deinit()
colorama.init(convert=False, strip=False)


shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)
exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)
install(include="friendly_tb")

# By default, we assume a terminal with a dark background.
set_formatter("dark")  # noqa
__all__ = list(helpers.keys())

print(
    f"friendly_traceback {__version__}; friendly {version}.\nType 'Friendly' for information."
)
