from ._ipython import *  # noqa
from ._ipython import version
from friendly_traceback import __version__

# We do not want to install Rich so that %pprint will work
set_formatter("repl")  # noqa
print(
    f"friendly_traceback {__version__}; friendly {version}.\nType 'Friendly' for information."
)
