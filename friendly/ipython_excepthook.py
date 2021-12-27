"""Automatically installs Friendly as a replacement for the standard traceback in IPython.

Used in IPython itself and other programming environments based on IPython such as
Jupyter, Google Colab, Mu's repl, etc.
"""

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
)  # noqa

import colorama

try:
    from IPython.core import compilerop, interactiveshell
except ImportError:
    raise ValueError("IPython cannot be imported.")
try:
    from IPython.utils import py3compat  # noqa
except ImportError:
    pass
else:
    exclude_file_from_traceback(py3compat.__file__)

exclude_file_from_traceback(interactiveshell.__file__)
exclude_file_from_traceback(compilerop.__file__)

colorama.deinit()
colorama.init(convert=False, strip=False)

interactiveshell.InteractiveShell.showtraceback = (
    lambda self, *args, **kwargs: explain_traceback()
)
interactiveshell.InteractiveShell.showsyntaxerror = (
    lambda self, *args, **kwargs: explain_traceback()
)
install(include="friendly_tb")
