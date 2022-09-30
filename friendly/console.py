"""
console.py
==========

Adaptation of Python's console found in code.py so that it can be
used to show some "friendly" tracebacks.
"""
import platform

import friendly_traceback as ft

from friendly_traceback import ft_console, friendly_exec
from friendly_traceback.config import session
from friendly.rich_console_helpers import helpers
from .my_gettext import current_lang

import friendly


BANNER = "\nfriendly-traceback: {}\nfriendly: {}\nPython: {}\n".format(
    ft.__version__, friendly.__version__, platform.python_version()
)

_ = current_lang.translate


class FriendlyConsole(ft_console.FriendlyTracebackConsole):
    # skipcq: PYL-W0622
    def __init__(
        self,
        local_vars=None,
        formatter="dark",
        background=None,
        displayhook=None,
        ipython_prompt=True,
    ):
        """This class builds upon Python's code.InteractiveConsole
        to provide friendly tracebacks. It keeps track
        of code fragment executed by treating each of them as
        an individual source file.
        """
        super().__init__(
            local_vars=local_vars,
            displayhook=displayhook,
            ipython_prompt=ipython_prompt,
        )
        self.rich_console = False
        friendly.set_formatter(formatter, background=background)
        if formatter in ["dark", "light"]:
            self.rich_console = True

    def raw_input(self, prompt=""):
        """Write a prompt and read a line.
        The returned line does not include the trailing newline.
        When the user enters the EOF key sequence, EOFError is raised.
        The base implementation uses the built-in function
        input(); a subclass may replace this with a different
        implementation.
        """
        if self.rich_console:
            if "[" in prompt:
                prompt = f"\n[operators][[/operators]{self.counter}[operators]]: "
            elif "...:" in prompt:
                prompt = prompt.replace("...:", "...[operators]:[/operators]")
            else:
                prompt = "[operators]" + prompt
            return session.console.input(prompt)
        return input(prompt)


def start_console(
    local_vars=None,
    formatter=None,
    include="friendly_tb",
    lang=None,
    banner=None,
    background=None,
    displayhook=None,
    ipython_prompt=True,
):
    """Starts a console; modified from code.interact"""
    if friendly.settings.ENVIRONMENT is None:
        if friendly.settings.terminal_type:
            friendly.settings.ENVIRONMENT = friendly.settings.terminal_type
        else:
            friendly.settings.ENVIRONMENT = "terminal"

    if lang is None:
        lang = friendly.get_lang()
    if banner is None:
        banner = BANNER + ft.ft_console.type_friendly() + "\n"
    if formatter is None:
        formatter = friendly.settings.read(option="formatter")
        if formatter is None:
            formatter = "dark"
    if background is None:
        background = friendly.settings.read(option="background")

    friendly.set_lang(lang)

    if not ft.is_installed():
        ft.install(include=include, lang=lang)

    if local_vars is not None:
        # Make sure we don't overwrite with our own functions
        helpers.update(local_vars)
    helpers["friendly_exec"] = friendly_exec

    console = FriendlyConsole(
        local_vars=helpers,
        formatter=formatter,
        background=background,
        displayhook=displayhook,
        ipython_prompt=ipython_prompt,
    )
    console.interact(banner=banner)
