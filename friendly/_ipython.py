"""Experimental module to automatically install Friendly
as a replacement for the standard traceback in IPython."""

try:
    from IPython.core import interactiveshell as shell  # noqa
    from IPython.core import compilerop, magic  # noqa
except ImportError:
    raise ValueError("IPython cannot be imported.")

import colorama

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
    current_lang,
)  # noqa

from friendly_traceback.config import session

from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import helpers  # noqa
from friendly import __version__ as version  # noqa

try:
    from IPython.utils import py3compat  # noqa

    exclude_file_from_traceback(py3compat.__file__)
except Exception:  # noqa
    pass

colorama.deinit()
colorama.init(convert=False, strip=False)
session.ipython_prompt = True
_ = current_lang.translate


shell.InteractiveShell.showtraceback = lambda self, *args, **kwargs: explain_traceback()
shell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)
exclude_file_from_traceback(shell.__file__)
exclude_file_from_traceback(compilerop.__file__)
install(include="friendly_tb")


@magic.register_line_cell_magic
def pprint(_line=None, _cell=None):
    print(
        _(
            "%pprint is not supported by Rich (used by friendly).\n"
            "If you absolutely need to use %pprint, import friendly.ipython_plain\n"
            "instead of friendly.ipython."
        )
    )
