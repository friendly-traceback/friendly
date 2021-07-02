"""
friendly.__init__.py
==============================

With the exceptions of the functions that are specific to the console,
this module contains all the functions that are part of the public API.
While Friendly is still considered to be in alpha stage,
we do attempt to avoid creating incompatibility for the functions
here when introducing changes.

The goal is to be even more careful to avoid introducing incompatibilities
when reaching beta stage, and planning to be always backward compatible
starting at version 1.0 -- except possibly for the required minimal
Python version.

Friendly is currently compatible with Python versions 3.6
or newer.

If you find that some additional functionality would be useful to
have as part of the public API, please let us know.
"""
import sys

valid_version = sys.version_info.major >= 3 and sys.version_info.minor >= 6

if not valid_version:  # pragma: no cover
    print("Python 3.6 or newer is required.")
    sys.exit()

del valid_version
__version__ = "0.3.142a"


# ===========================================

import inspect
from pathlib import Path

from friendly_traceback import editors_helpers
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback.config import session
from .my_gettext import current_lang


def run(
    filename,
    lang=None,
    include=None,
    args=None,
    console=True,
    formatter="bw",
    redirect=None,
    background=None,
):
    """Given a filename (relative or absolute path) ending with the ".py"
    extension, this function uses the
    more complex ``exec_code()`` to run a file.

    If console is set to ``False``, ``run()`` returns an empty dict
    if a ``SyntaxError`` was raised, otherwise returns the dict in
    which the module (``filename``) was executed.

    If console is set to ``True`` (the default), the execution continues
    as an interactive session in a Friendly console, with the module
    dict being used as the locals dict.

    Other arguments include:

    ``lang``: language used; currently only ``'en'`` (default) and ``'fr'``
    are available.

    ``include``: specifies what information is to be included if an
    exception is raised; the default is ``"friendly_tb"`` if console
    is set to ``True``, otherwise it is ``"explain"``

    ``args``: strings tuple that is passed to the program as though it
    was run on the command line as follows::

        python filename.py arg1 arg2 ...

    ``use_rich``: ``False`` by default. Set it to ``True`` if Rich is available
    and the environment supports it.

    ``theme``: Theme to be used with Rich. Currently only ``"dark"``,
    the default, and ``"light"`` are available. ``"light"`` is meant for
    light coloured background and has not been extensively tested.
    """
    _ = current_lang.translate
    if include is None:
        include = "friendly_tb" if console else "explain"
    if args is not None:
        sys.argv = [filename, *list(args)]
    else:
        filename = Path(filename)
        if not filename.is_absolute():
            frame = inspect.stack()[1]
            # This is the file from which run() is called
            run_filename = Path(frame[0].f_code.co_filename)
            run_dir = run_filename.parent.absolute()
            filename = run_dir.joinpath(filename)

        if not filename.exists():
            print(_("The file {filename} does not exist.").format(filename=filename))
            return

    session.install(lang=lang, include=include, redirect=redirect)
    session.set_formatter(formatter)

    module_globals = editors_helpers.exec_code(
        path=filename, lang=lang, include=include
    )
    if console:  # pragma: no cover
        start_console(
            local_vars=module_globals,
            formatter=formatter,
            banner="",
            include=include,
            background=background,
        )
    else:
        return module_globals


def set_formatter(formatter=None, **kwargs):
    """Sets the default formatter. If no argument is given, the default
    formatter is used.

    A custom formatter must accept ``info`` as a required arguments
    as well an additional argument whose value is subject to change.
    See formatters.py for details.
    """
    ft_set_formatter(formatter=formatter)
    # session.set_formatter(formatter=formatter, **kwargs)


def start_console(  # pragma: no cover
    local_vars=None,
    formatter="bw",
    include="friendly_tb",
    lang="en",
    banner=None,
    color_schemes=None,
    background=None,
    displayhook=None,
):
    """Starts a Friendly console."""
    from . import console

    console.start_console(
        local_vars=local_vars,
        formatter=formatter,
        include=include,
        lang=lang,
        banner=banner,
        color_schemes=color_schemes,
        background=background,
        displayhook=displayhook,
    )


# def _include_choices():
#     """Prints the available choices for arguments to set_include()"""
#     choices = [repr(key) for key in formatters.items_groups if key != "header"]
#     return ",\n        ".join(choices)


# def set_include(include):
#     """Specifies the information to include in the traceback.

#     The allowed values are:

#         {choices}
#     """
#     session.set_include(include)


# if set_include.__doc__ is not None:  # protect against -OO optimization
#     set_include.__doc__ = set_include.__doc__.format(choices=_include_choices())
