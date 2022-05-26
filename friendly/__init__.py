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
import os
import sys

valid_version = sys.version_info >= (3, 6, 1)

if not valid_version:  # pragma: no cover
    # Rich does not support 3.6.0
    print("Python 3.6.1 or newer is required.")
    sys.exit()

del valid_version
__version__ = "0.5.24"


# ===========================================

import inspect
from pathlib import Path

from .my_gettext import current_lang
from friendly import rich_formatters, theme, settings

from friendly_traceback import (
    editors_helpers,
    exclude_directory_from_traceback,
    set_stream,
)
from friendly_traceback import explain_traceback as ft_explain_traceback
from friendly_traceback import install as ft_install
from friendly_traceback import set_formatter as ft_set_formatter
from friendly_traceback import set_lang as ft_set_lang
from friendly_traceback import __version__ as ft_version
from friendly_traceback.config import session

# The following are not used here, and simply made available directly for convenience
from friendly_traceback import (  # noqa
    exclude_file_from_traceback,
    get_include,
    get_output,
    get_stream,
    set_include,
)


exclude_directory_from_traceback(os.path.dirname(__file__))
get_lang = current_lang.get_lang


def install(lang=None, formatter=None, redirect=None, include="explain", _debug=None):
    """
    Replaces ``sys.excepthook`` by friendly's own version.
    Intercepts, and can provide an explanation for all Python exceptions except
    for ``SystemExist`` and ``KeyboardInterrupt``.

    The optional arguments are:

        lang: language to be used for translations. If not available,
              English will be used as a default.

        formatter: if desired, sets a specific formatter to use.

        redirect: stream to be used to send the output.
                  The default is sys.stderr

        include: controls the amount of information displayed.
        See set_include() for details.
    """
    # Note: need "explain" since there is no interaction possible with install
    if lang is None:
        lang = get_lang()
    set_formatter(formatter=formatter)
    ft_install(lang=lang, redirect=redirect, include=include, _debug=_debug)


def explain_traceback(formatter=None, redirect=None):
    """Replaces a standard traceback by a friendlier one, giving more
    information about a given exception than a standard traceback.
    Note that this excludes ``SystemExit`` and ``KeyboardInterrupt``
    which are re-raised.

    If no formatter is specified, the default one will be used.

    By default, the output goes to ``sys.stderr`` or to some other stream
    set to be the default by another API call. However, if::

       redirect = some_stream

    is specified, the output goes to that stream, but without changing
    the global settings.

    If the string ``"capture"`` is given as the value for ``redirect``, the
    output is saved and can be later retrieved by ``get_output()``.
    """
    set_formatter(formatter=formatter)
    ft_explain_traceback(redirect=redirect)


def run(
    filename,
    lang=None,
    include=None,
    args=None,
    console=True,
    formatter=None,
    redirect=None,
    background=None,
    ipython_prompt=True,
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

    ``theme``: Theme to be used with Rich. Currently, only ``"dark"``,
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
    set_lang(lang)
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
            ipython_prompt=ipython_prompt,
        )
    else:
        return module_globals


def set_formatter(
    formatter=None, color_system="auto", force_jupyter=None, background=None
):
    """Sets the default formatter. If no argument is given, a default
    formatter is used.
    """
    if formatter is not None:
        settings.write(option="formatter", value=formatter)
        if background is not None:
            background = theme.colours.set_background_color(background)
        else:
            old_background = settings.read(option="background")
            if (
                formatter == settings.read(option="formatter")
                and old_background is not None
            ):
                background = old_background
    elif background is not None:
        background = theme.colours.set_background_color(background)
        old_formatter = settings.read(option="formatter")
        if old_formatter is None:
            return
        formatter = old_formatter
        old_color_system = settings.read(option="color_system")
        if old_color_system is not None:
            color_system = old_color_system
        old_force_jupyter = settings.read(option="force_jupyter")
        if old_force_jupyter is not None:
            force_jupyter = old_force_jupyter

    if color_system is not None:
        settings.write(option="color_system", value=color_system)
    if force_jupyter is not None:
        settings.write(option="force_jupyter", value=force_jupyter)

    session.rich_add_vspace = True
    session.use_rich = True
    session.jupyter_button_style = ""
    set_stream()
    if isinstance(formatter, str):
        settings.write(option="formatter", value=formatter)
    if formatter in ["dark", "light"]:
        session.console = theme.init_rich_console(
            style=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        set_stream(redirect=rich_formatters.rich_writer)
        formatter = rich_formatters.rich_markdown
    elif formatter == "interactive-dark":
        session.console = theme.init_rich_console(
            style="dark",
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        formatter = rich_formatters.jupyter_interactive
        session.jupyter_button_style = ";color:white; background-color:#101010;"
    elif formatter in ["interactive", "interactive-light"]:
        session.console = theme.init_rich_console(
            style="light",
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
        formatter = rich_formatters.jupyter_interactive
    elif formatter == "jupyter":
        formatter = rich_formatters.jupyter
        session.use_rich = False
        theme.disable_rich()
    else:
        session.use_rich = False
        set_stream()
        theme.disable_rich()
        if formatter == "plain":
            formatter = "repl"
    ft_set_formatter(formatter=formatter)


def start_console(  # pragma: no cover
    local_vars=None,
    formatter=None,
    include="friendly_tb",
    lang=None,
    banner=None,
    background=None,
    displayhook=None,
    ipython_prompt=True,
):
    """Starts a Friendly console."""
    from . import console

    console.start_console(
        local_vars=local_vars,
        formatter=formatter,
        include=include,
        lang=lang,
        banner=banner,
        background=background,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )


def set_lang(lang):
    """Sets the language to be used."""
    ft_set_lang(lang)
    settings.write(option="lang", value=lang, environment="common")
    current_lang.install(lang)


set_lang(get_lang())


def _print_settings():
    """View all saved values"""
    settings.print_settings()


def print_repl_header():
    """Prints the header at the beginning of an interactive session."""
    _ = current_lang.translate
    print(f"friendly_traceback {ft_version}; friendly {__version__}.")
    print(_("Type 'Friendly' for basic help."))
