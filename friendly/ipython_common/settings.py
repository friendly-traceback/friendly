from friendly import settings
from friendly_traceback import config
from friendly.rich_console_helpers import set_formatter


def init_settings(default_formatter="dark"):
    """Initialises the formatter using saved settings for the
    current environment.
    """
    if settings.has_environment(settings.ENVIRONMENT):
        formatter = settings.read(option="formatter")
        background = settings.read(option="background")
        color_system = settings.read(option="color_system")
        force_jupyter = settings.read(option="force_jupyter")
        set_formatter(
            formatter=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
    else:
        set_formatter(default_formatter)

    if settings.has_environment(settings.ENVIRONMENT):
        _ipython_prompt = settings.read(option="ipython_prompt")
        if _ipython_prompt in [None, "True"]:
            config.session.ipython_prompt = True
        else:
            config.session.ipython_prompt = False
    else:
        config.session.ipython_prompt = True
        settings.write(option="ipython_prompt", value="True")
