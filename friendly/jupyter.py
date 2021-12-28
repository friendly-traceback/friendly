from rich import jupyter as rich_jupyter

"""Sets up everything required for an IPython terminal session."""
from friendly.ipython_common.excepthook import install_except_hook
from friendly.ipython_common.settings import init_settings

from friendly import print_repl_header
from friendly import settings
from friendly_traceback import config
from friendly.rich_console_helpers import *  # noqa

from friendly_traceback import session  # noqa
from friendly_traceback.functions_help import (
    add_help_attribute,
    short_description,
)  # noqa

# from .ipython import *  # noqa
from friendly.my_gettext import current_lang  # noqa
from friendly.rich_console_helpers import *  # noqa
from friendly.rich_console_helpers import helpers, Friendly

_ = current_lang.translate


if settings.terminal_type:
    settings.ENVIRONMENT = settings.terminal_type + "-jupyter"
else:
    settings.ENVIRONMENT = "jupyter"


# For Jupyter output, Rich specifies a set of fonts starting with Menlo and
# ending with monospace as last resort whereas Jupyter notebooks just
# specify monospace. To make font-size more consistent, we remove the
# font-specification from Rich.
rich_jupyter.JUPYTER_HTML_FORMAT = (
    "<pre style='white-space:pre;overflow-x:auto;line-height:normal'>{code}</pre>"
)
old_light = light  # noqa
old_dark = dark  # noqa


def light():
    set_formatter("interactive")  # noqa


def dark():
    set_formatter("interactive-dark")  # noqa


light.__doc__ = old_light.__doc__
Friendly.light = light  # noqa
helpers["light"] = light

dark.__doc__ = old_dark.__doc__
Friendly.dark = dark  # noqa
helpers["dark"] = dark


def set_tb_width(width=None):
    """Sets the width of the traceback when using a rich-based
    formatter in a Jupyter notebook or equivalent.

    The width of traceback is never less than the width of
    the other output from rich.
    """
    if width is None:
        return
    try:
        session.console.width = width
    except Exception:  # noqa
        return
    session.rich_tb_width = width
    if session.rich_width is None or session.rich_width > session.rich_tb_width:
        session.rich_width = width


short_description["set_tb_width"] = lambda: _("Sets the width of the traceback.")
add_help_attribute({"set_tb_width": set_tb_width})

Friendly.add_helper(set_tb_width)
helpers["set_tb_width"] = set_tb_width

__all__ = list(helpers.keys())

install_except_hook()
# Use the new interactive light formatter by default.
init_settings("interactive-light")
set_tb_width(100)  # noqa
set_width(70)  # noqa
session.is_jupyter = True
print_repl_header()
if config.did_exception_occur_before():
    friendly_tb()  # noqa
