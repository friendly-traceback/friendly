# flake8: noqa
import sys

if "InteractiveShell" in repr(sys.excepthook):
    from .repl import *
    from .repl import __all__

else:
    from .runner import *
    from .runner import __all__
