"""
main.py
---------------

Sets up the various options when Friendly is invoked from the
command line. You can find more details by doing::

    python -m friendly -h

"""
import argparse
import os
import platform
import runpy
import sys
import warnings

from importlib import import_module
from pathlib import Path

from friendly_traceback import explain_traceback, exclude_file_from_traceback, install
from friendly_traceback import __version__ as ft_version
from friendly_traceback import debug_helper

from friendly import console, __version__
from .my_gettext import current_lang

from friendly.rich_console_helpers import set_formatter


versions = "\nfriendly-traceback: {}\nfriendly: {}\nPython: {}\n".format(
    ft_version, __version__, platform.python_version()
)


def import_function(dotted_path: str) -> type:
    """Import a function from a module, given its dotted path.

    This is a utility function currently used when a custom formatter
    is invoked by a command line argument::

        python -m friendly --formatter custom_formatter
    """
    # Used by HackInScience.org
    try:
        module_path, function_name = dotted_path.rsplit(".", 1)
    except ValueError as err:  # pragma: no cover
        raise ImportError("%s doesn't look like a module path" % dotted_path) from err

    module = import_module(module_path)

    try:
        return getattr(module, function_name)
    except AttributeError as err:  # pragma: no cover
        raise ImportError(
            'Module "%s" does not define a "%s" function' % (module_path, function_name)
        ) from err


parser = argparse.ArgumentParser(
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=(
        """Friendly makes Python tracebacks easier to understand.

    {versions}

    If no source is given Friendly will start an interactive console.
        """.format(
            versions=versions
        )
    ),
)

parser.add_argument(
    "source",
    nargs="?",
    help="""Name of the Python script (path/to/my_program.py)
    to be run as though it was the main module, so that its
    __name__ does equal '__main__'.
    """,
)

parser.add_argument(
    "args",
    nargs="*",
    help="""Optional arguments to give to the script specified by source.
         """,
)

parser.add_argument(
    "--lang",
    default=current_lang.get_lang(),
    help="""This sets the language used by Friendly.
            Usually this is a two-letter code such as 'fr' for French.
         """,
)

parser.add_argument(
    "--version",
    help="""Only displays the current version.
         """,
    action="store_true",
)

parser.add_argument(
    "-f",
    "--formatter",
    help="""Specifies an output format (bw, dark, light, docs, markdown, or markdown_docs)
    or a custom formatter function, as a dotted path. By default, the console
    will use dark if it is available.

    For example: --formatter friendly.rich_formatters.markdown is
    equivalent to --formatter markdown
    """,
)

parser.add_argument(
    "--background",
    help="""Specifies a background color to be used if either the 'dark' or the 'light'
    formatter is specified.  The color needs to be specified as an hexadecimal
    value '#xxxxxx'. The default is black for 'dark' and white for 'light'.
    """,
)

parser.add_argument("--debug", help="""For developer use.""", action="store_true")
parser.add_argument("--no_debug", help="""For developer use.""", action="store_true")

parser.add_argument(
    "--include",
    help="""Specifies what content to include by default in the traceback.
    The defaults are 'friendly_tb' if the friendly-console is going to be shown,
    otherwise it is 'explain'.
    """,
)

parser.add_argument(
    "--python_prompt",
    help="""Specifies that the console prompt must the regular Python prompt""",
    action="store_true",
)

parser.add_argument(
    "-i", help="""Starts the console after executing a source""", action="store_true"
)


def main():
    _ = current_lang.translate
    sys.path.insert(0, os.getcwd())
    args = parser.parse_args()
    if args.version:  # pragma: no cover
        print(f"\nFriendly version {__version__}")
        if not args.source:
            sys.exit()

    include = "friendly_tb"
    if args.include:  # pragma: no cover
        include = args.include
    elif args.source and not (sys.flags.interactive or args.i):
        include = "explain"
    if args.debug:  # pragma: no cover
        debug_helper.DEBUG = True
        include = "debug_tb"
    elif args.no_debug:  # pragma: no cover
        debug_helper.DEBUG = False

    install(lang=args.lang, include=include)

    if args.formatter:
        formatter = args.formatter  # noqa
        if formatter in ["repl", "dark", "light", "docs"]:
            set_formatter(formatter, background=args.background)  # pragma: no cover
        else:
            set_formatter(import_function(args.formatter))
    else:
        set_formatter("dark", background=args.background)  # pragma: no cover
    console_defaults = {}
    if args.source is not None:
        filename = Path(args.source)
        if not filename.exists():  # pragma: no cover
            print(
                "\n",
                _("The file {filename} does not exist.").format(filename=args.source),
            )
            return

        exclude_file_from_traceback(runpy.__file__)
        sys.argv = [args.source, *args.args]
        if not (sys.flags.interactive or args.i):
            warnings.simplefilter("ignore")
        try:
            module_dict = runpy.run_path(args.source, run_name="__main__")
            console_defaults.update(module_dict)
        except Exception:  # noqa
            explain_traceback()
        if sys.flags.interactive or args.i:  # pragma: no cover
            console.start_console(
                local_vars=console_defaults,
                background=args.background,
                lang=args.lang,
                ipython_prompt=not args.python_prompt,
            )

    else:  # pragma: no cover
        console.start_console(
            local_vars=console_defaults,
            background=args.background,
            lang=args.lang,
            ipython_prompt=not args.python_prompt,
        )


if __name__ == "__main__":
    main()
