"""Experimental module to automatically install Friendly
as a replacement for the standard traceback in IPython."""
import sys

try:
    from IPython.core import interactiveshell as shell  # noqa
    from IPython.core import compilerop, magic  # noqa
    from IPython.core.formatters import PlainTextFormatter  # noqa
except ImportError:
    raise ValueError("IPython cannot be imported.")

import colorama

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
    __version__,
)  # noqa

from friendly_traceback.config import session, did_exception_occur_before
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import helpers, current_lang  # noqa
from friendly import __version__ as version  # noqa
from friendly import current_lang  # noqa
from friendly import configuration

try:
    from IPython.utils import py3compat  # noqa

    exclude_file_from_traceback(py3compat.__file__)
except Exception:  # noqa
    pass

_ = current_lang.translate
colorama.deinit()
colorama.init(convert=False, strip=False)
session.ipython_prompt = True
configuration.ENVIRONMENT = "ipython"

shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)
exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)
install(include="friendly_tb")

# By default, we assume a terminal with a dark background.
set_formatter("dark")  # noqa
print(
    f"friendly_traceback {__version__}; friendly {version}."
)

if not session.exception_before_import:
    if did_exception_occur_before():
        friendly_tb()
print(_("Type 'Friendly' for basic help."))