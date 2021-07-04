from friendly_traceback.console_helpers import *  # noqa
from friendly_traceback.console_helpers import FriendlyHelpers, helpers
from friendly_traceback.utils import add_rich_repr
from friendly_traceback.config import session

from friendly.my_gettext import current_lang
from friendly import set_formatter

_ = current_lang.translate


def dark():  # pragma: no cover
    """Synonym of set_formatter('dark') designed to be used
    within iPython/Jupyter programming environments or at a terminal.
    """
    set_formatter("dark")


def light():  # pragma: no cover
    """Synonym of set_formatter('light') designed to be used
    within iPython/Jupyter programming environments or at a terminal.
    """
    set_formatter("light")


dark.help = lambda: _("Sets a colour scheme designed for a black background.")
light.help = lambda: _("Sets a colour scheme designed for a white background.")

default_color_schemes = {"dark": dark, "light": light}
add_rich_repr(default_color_schemes)

old_history = history  # noqa


def history():
    session.rich_add_vspace = False
    old_history()
    session.rich_add_vspace = True


history.help = old_history.help  # noqa
history.__rich_repr__ = old_history.__rich_repr__  # noqa
history.__doc__ = old_history.__doc__
FriendlyHelpers.history = history

for scheme in default_color_schemes:
    setattr(FriendlyHelpers, scheme, staticmethod(default_color_schemes[scheme]))
Friendly = FriendlyHelpers(local_helpers=default_color_schemes)

helpers["Friendly"] = Friendly
helpers["history"] = history

__all__ = list(helpers.keys())
__all__.extend(list(default_color_schemes))
