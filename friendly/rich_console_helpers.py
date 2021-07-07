"""In this module, we modify the basic console helpers for friendly-traceback
so as to add custom ones for Rich-based formatters."""

from friendly_traceback.console_helpers import *  # noqa

old_set_formatter = set_formatter  # noqa
old_history = history  # noqa

from friendly_traceback.console_helpers import FriendlyHelpers, helpers
from friendly_traceback.utils import add_rich_repr
from friendly_traceback.config import session

from friendly.my_gettext import current_lang
from friendly import set_formatter

_ = current_lang.translate

# =============================================
# Modifying existing console helpers
# =============================================

set_formatter.help = old_set_formatter.help  # noqa
set_formatter.__rich_repr__ = old_set_formatter.__rich_repr__  # noqa
FriendlyHelpers.set_formatter = set_formatter
helpers["set_formatter"] = set_formatter


def history():
    session.rich_add_vspace = False
    old_history()
    session.rich_add_vspace = True


history.help = old_history.help  # noqa
history.__rich_repr__ = old_history.__rich_repr__  # noqa
history.__doc__ = old_history.__doc__
FriendlyHelpers.history = history
helpers["history"] = history

# =================================
# Additional rich-specific helpers
# =================================


def dark():
    """Synonym of set_formatter('dark') designed to be used
    within iPython/Jupyter programming environments.
    """
    set_formatter("dark")


def light():
    """Synonym of set_formatter('light') designed to be used
    within iPython/Jupyter programming environments.
    """
    set_formatter("light")


def set_width(width=80):
    """Sets the width in a iPython/Jupyter session using 'light' or 'dark' mode"""
    if session.use_rich:
        session.console._width = width
    else:
        print(_("set_width() is only available using 'light' or 'dark' mode."))


dark.help = lambda: _("Sets a colour scheme designed for a black background.")
light.help = lambda: _("Sets a colour scheme designed for a white background.")
set_width.help = lambda: "Sets the output width in 'light' or 'dark' mode."

local_helpers = {"dark": dark, "light": light, "set_width": set_width}
add_rich_repr(local_helpers)

for helper in local_helpers:
    setattr(FriendlyHelpers, helper, staticmethod(local_helpers[helper]))
Friendly = FriendlyHelpers(local_helpers=local_helpers)

helpers["Friendly"] = Friendly
helpers.update(local_helpers)
__all__ = list(helpers.keys())
