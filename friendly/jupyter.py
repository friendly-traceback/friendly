from rich import jupyter as rich_jupyter

from friendly_traceback import session  # noqa
from friendly_traceback.functions_help import (
    add_help_attribute,
    short_description,
)  # noqa
from .ipython import *  # noqa
from .ipython import helpers, Friendly
from friendly import rich_formatters
from friendly.my_gettext import current_lang
from friendly_traceback import config

_ = current_lang.translate

# For Jupyter output, Rich specifies a set of fonts starting with Menlo and
# ending with monospace as last resort whereas Jupyter notebooks just
# specify monospace. To make font-size more consistent, we remove the
# font-specification from Rich.
rich_jupyter.JUPYTER_HTML_FORMAT = (
    "<pre style='white-space:pre;overflow-x:auto;line-height:normal'>{code}</pre>"
)
old_set_formatter = set_formatter  # noqa
old_light = light  # noqa
old_dark = dark  # noqa


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    session.rich_add_vspace = False
    session.use_rich = True
    if formatter == "jupyter":
        set_formatter(rich_formatters.jupyter)
    else:
        old_set_formatter(
            formatter=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )


helpers["set_formatter"] = set_formatter
Friendly.set_formatter = set_formatter  # noqa


def light():
    set_formatter("interactive")


def dark():
    set_formatter("interactive-dark")


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
        print(_("set_width() has no effect with this formatter."))
        return
    session.rich_tb_width = width
    if session.rich_width is None or session.rich_width > session.rich_tb_width:
        session.rich_width = width


short_description["set_tb_width"] = lambda: _("Sets the width of the traceback.")
add_help_attribute({"set_tb_width": set_tb_width})

Friendly.add_helper(set_tb_width)
helpers["set_tb_width"] = set_tb_width

__all__ = list(helpers.keys())

# Use the new interactive light formatter by default.

light()  # noqa
set_tb_width(100)  # noqa
set_width(70)  # noqa
session.is_jupyter = True

if config.did_exception_occur_before():
    friendly_tb()  # noqa
