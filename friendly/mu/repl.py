"""Mu's repl uses an IPython QtConsole.
Mu has three themes designated (in English) as 'day', 'night',
and 'high contrast'."""

import colorama  # noqa
from friendly_traceback import set_stream
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback.config import session  # noqa
from friendly_traceback.utils import add_rich_repr  # noqa

from ..my_gettext import current_lang  # noqa
from friendly.ipython import *  # noqa  # Will automatically install

old_set_width = set_width  # noqa
from friendly import set_formatter as old_set_formatter
from friendly.rich_console_helpers import FriendlyHelpers, helpers


from friendly import theme
from friendly import rich_formatters

colorama.deinit()  # reset needed on Windows
colorama.init(convert=False, strip=False)

_ = current_lang.translate

del helpers["dark"]
del helpers["light"]


def set_formatter(formatter=None, background=None):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    if formatter in ["black", "day", "night"]:
        style = "light" if formatter == "day" else "dark"
        session.console = theme.init_rich_console(
            style=style,
            color_system="truecolor",
            force_jupyter=False,
            background=background,
        )
        session.use_rich = True
        session.rich_add_vspace = True
        formatter = rich_formatters.rich_markdown
        set_stream(redirect=rich_formatters.rich_writer)
    else:
        session.use_rich = False
        session.rich_add_vspace = False
        set_stream()
    ft_set_formatter(formatter=formatter)


set_formatter.help = old_set_formatter.help  # noqa
set_formatter.__rich_repr__ = old_set_formatter.__rich_repr__  # noqa
FriendlyHelpers.set_formatter = set_formatter
helpers["set_formatter"] = set_formatter


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using 'light' or 'dark' mode"""
    if session.use_rich:
        session.console._width = width
    else:
        print(_("set_width() is only available using 'day', 'night' or 'black' mode."))


set_width.help = old_set_width.help  # noqa
set_width.__rich_repr__ = old_set_width.__rich_repr__  # noqa
setattr(FriendlyHelpers, "set_width", set_width)
helpers["set_width"] = set_width


def day():
    """Day theme for Mu's REPL"""
    set_formatter("day", background="#FEFEF7")


def night():
    """Night theme for Mu's REPL"""
    set_formatter("night", background="#373737")


def black():
    """Colourful theme with black background."""
    set_formatter("black", background="#000000")


def bw():
    """Black and white."""
    set_formatter("repl", background="#000000")


day.help = lambda: _("Colour scheme designed for Mu's day theme.")
night.help = lambda: _("Colour scheme designed for Mu's night theme.")
black.help = lambda: _("Colourful scheme designed for Mu's high contrast theme.")
bw.help = lambda: _("Black and white scheme designed for Mu's high contrast theme.")

local_helpers = {"day": day, "night": night, "black": black, "bw": bw}
add_rich_repr(local_helpers)

for helper in local_helpers:
    setattr(FriendlyHelpers, helper, staticmethod(local_helpers[helper]))
Friendly = FriendlyHelpers(local_helpers=local_helpers)

helpers["Friendly"] = Friendly
helpers.update(local_helpers)
__all__ = list(helpers.keys())
day()
