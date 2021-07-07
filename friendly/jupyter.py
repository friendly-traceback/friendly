from friendly_traceback import session  # noqa
from .ipython import *  # noqa
from .ipython import helpers
from friendly import rich_formatters

old_set_formatter = set_formatter  # noqa


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
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

# While the 'light' and 'dark' formatters produce better output
# when the corresponding jupyter theme is selected by the user,
# we have no way to determine the theme used.
# The jupyter formatter uses IPython custom methods so that the
# colours used automatically adjust based on the jupyter theme,
# and is thus always a suitable, if not ideal choice.
set_formatter("jupyter")  # noqa
