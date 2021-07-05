from friendly_traceback import session  # noqa
from .ipython import *  # noqa
from .ipython import helpers
from friendly import rich_formatters

old_set_formatter = set_formatter  # noqa


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, the default
    formatter is used.

    A custom formatter must accept ``info`` as a required arguments
    as well an additional argument whose value is subject to change.
    See formatters.py for details.
    """
    session.rich_add_vspace = True
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


set_formatter.help = old_set_formatter.help
set_formatter.__rich_repr__ = old_set_formatter.__rich_repr__
helpers["set_formatter"] = set_formatter
Friendly.set_formatter = set_formatter  # noqa

__all__ = list(helpers.keys())

set_formatter("jupyter")  # noqa
