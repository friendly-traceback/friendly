"""
console.py
==========

Adaptation of Python's console found in code.py so that it can be
used to show some "friendly" tracebacks.
"""
import builtins
import copy
import platform

import friendly_traceback as ft

from friendly_traceback import ft_console
from friendly_traceback.config import session
from friendly.rich_console_helpers import helpers
from .my_gettext import current_lang

import friendly
from . import theme

BANNER = "\nfriendly-traceback: {}\nfriendly: {}\nPython: {}\n".format(
    ft.__version__, friendly.__version__, platform.python_version()
)

please_comment = (
    "   Do you find these warnings useful?\n"
    "   Comment at https://github.com/friendly-traceback/friendly-traceback/issues/7.\n\n"
    "   You can use www('warnings') to go to that url."
)


class FriendlyConsole(ft_console.FriendlyTracebackConsole):
    # skipcq: PYL-W0622
    def __init__(
        self,
        local_vars=None,
        formatter="dark",
        background=None,
        displayhook=None,
        numbered_prompt=False,
    ):
        """This class builds upon Python's code.InteractiveConsole
        so as to provide friendly tracebacks. It keeps track
        of code fragment executed by treating each of them as
        an individual source file.
        """
        super().__init__(
            local_vars=local_vars,
            displayhook=displayhook,
            numbered_prompt=numbered_prompt,
        )

        self.old_locals = {}
        self.saved_builtins = {}
        for name in dir(builtins):
            self.saved_builtins[name] = getattr(builtins, name)
        self.rich_console = False
        friendly.set_formatter(formatter, background=background)
        if formatter in ["dark", "light"]:
            self.rich_console = session.console
        self.check_for_builtins_changes()
        self.check_for_annotations()

    def runcode(self, code):
        """Execute a code object.

        When an exception occurs, ft.explain_traceback() is called to
        display a traceback.  All exceptions are caught except
        SystemExit, which, unlike the case for the original version in the
        standard library, cleanly exists the program. This is done
        so as to avoid our Friendly's exception hook to intercept
        it and confuse the users.

        A note about KeyboardInterrupt: this exception may occur
        elsewhere in this code, and may not always be caught.  The
        caller should be prepared to deal with it.
        """
        super().runcode(code)
        self.check_for_builtins_changes()
        self.check_for_annotations()
        self.old_locals = copy.copy(self.locals)

    def check_for_annotations(self):
        """Attempts to detect code that uses : instead of = by mistake"""
        _ = current_lang.translate
        if "__annotations__" not in self.locals:
            return

        hints = self.locals["__annotations__"]
        if not hints:
            return

        warning_builtins = _(
            "Warning: you added a type hint to the python builtin `{name}`."
        )
        header_warning = _(
            "Warning: you used a type hint for a variable without assigning it a value.\n"
        )
        suggest_str = _("Instead of `{hint}`, perhaps you meant `{assignment}`.")

        for name in hints:
            if name in dir(builtins):
                warning = warning_builtins.format(name=name)
                if self.rich_console:
                    warning = "#### " + warning
                    warning = theme.friendly_rich.Markdown(warning)
                    self.rich_console.print(warning)
                    self.rich_console.print(please_comment)
                else:
                    print(warning)
                    print(please_comment)

        wrote_title = False
        warning = ""

        for name in hints:
            if name in dir(builtins):  # Already taken care of these above
                continue
            if (
                name not in self.locals
                or name in self.old_locals
                and self.old_locals[name] == self.locals[name]
            ):
                if not wrote_title:
                    warning = header_warning
                    wrote_title = True
                    if self.rich_console:
                        warning = "#### " + warning
                if not str(f"{hints[name]}").startswith("<"):
                    suggest = suggest_str.format(
                        hint=f"{name} : {hints[name]}",
                        assignment=f"{name} = {hints[name]}",
                    )
                else:
                    suggest = ""
                if self.rich_console and suggest:
                    suggest = "* " + suggest
                if suggest:
                    warning = warning + suggest + "\n"

        if warning:
            if self.rich_console:
                warning = theme.friendly_rich.Markdown(warning)
                self.rich_console.print(warning)
                self.rich_console.print(please_comment)
            else:
                print(warning)
                print(please_comment)

            self.locals["__annotations__"] = {}

    def check_for_builtins_changes(self):
        """Warning users if they assign a value to a builtin"""
        _ = current_lang.translate
        changed = []
        for name in self.saved_builtins:
            if name.startswith("__") and name.endswith("__"):
                continue

            if (
                name == "pow"
                and "cos" in self.locals
                and "cosh" in self.locals
                and "pi" in self.locals
            ):
                # we likely did 'from math import *' which redefines pow;
                # no warning needed in this case
                continue
            if name in self.locals and self.saved_builtins[name] != self.locals[name]:
                warning = _(
                    "Warning: you have redefined the python builtin `{name}`."
                ).format(name=name)
                if self.rich_console:
                    warning = theme.friendly_rich.Markdown("#### " + warning)
                    self.rich_console.print(warning)
                    self.rich_console.print(please_comment)
                else:
                    print(warning)
                    print(please_comment)
                changed.append(name)

        for name in changed:
            self.saved_builtins[name] = self.locals[name]

    # The following two methods are never used in this class, but they are
    # defined in the parent class. The following are the equivalent methods
    # that can be used if an explicit call is desired for some reason.

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.
        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.
        The base implementation uses the built-in function
        input(); a subclass may replace this with a different
        implementation.
        """
        if self.rich_console:
            self.rich_console.print(prompt, style="operators", end="")
            return input()
        return input(prompt)


def start_console(
    local_vars=None,
    formatter="dark",
    include="friendly_tb",
    lang="en",
    banner=None,
    background=None,
    displayhook=None,
    numbered_prompt=False,
):
    """Starts a console; modified from code.interact"""
    # from . import config

    if banner is None:
        banner = BANNER + ft.ft_console.type_friendly() + "\n"

    if not ft.is_installed():
        ft.install(include=include, lang=lang)

    if local_vars is not None:
        # Make sure we don't overwrite with our own functions
        helpers.update(local_vars)

    console = FriendlyConsole(
        local_vars=helpers,
        formatter=formatter,
        background=background,
        displayhook=displayhook,
        numbered_prompt=numbered_prompt,
    )
    console.interact(banner=banner)
