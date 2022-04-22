"""Automatically installs Friendly as a replacement for the standard traceback in IPython.

Used in IPython itself and other programming environments based on IPython such as
Jupyter, Google Colab, Mu's repl, etc.
"""

from friendly_traceback import (
    install,
    exclude_file_from_traceback,
    explain_traceback,
    uninstall,
)  # noqa

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


original_exception_hooks = {}


def enable():
    """Installs friendly-traceback as an exception hook in IPython"""
    # save old values
    original_exception_hooks[
        "showtraceback"
    ] = interactiveshell.InteractiveShell.showtraceback
    original_exception_hooks[
        "showsyntaxerror"
    ] = interactiveshell.InteractiveShell.showsyntaxerror
    interactiveshell.InteractiveShell.showtraceback = (
        lambda self, *args, **kwargs: explain_traceback()
    )
    interactiveshell.InteractiveShell.showsyntaxerror = (
        lambda self, *args, **kwargs: explain_traceback()
    )
    install(include="friendly_tb")


def disable():
    if not original_exception_hooks:
        print("friendly is not installed.")
        return
    uninstall()
    interactiveshell.InteractiveShell.showtraceback = original_exception_hooks[
        "showtraceback"
    ]
    interactiveshell.InteractiveShell.showsyntaxerror = original_exception_hooks[
        "showsyntaxerror"
    ]
    original_exception_hooks.clear()
