from friendly import configuration
from friendly_traceback import config
from friendly.rich_console_helpers import set_formatter


def init_configuration(default_formatter="dark"):
    """Initialises the formatter using saved configurations for the
    current environment.
    """
    if configuration.has_environment(configuration.ENVIRONMENT):
        formatter = configuration.read(option="formatter")
        background = configuration.read(option="background")
        color_system = configuration.read(option="color_system")
        force_jupyter = configuration.read(option="force_jupyter")
        set_formatter(
            formatter=formatter,
            color_system=color_system,
            force_jupyter=force_jupyter,
            background=background,
        )
    else:
        set_formatter(default_formatter)

    if configuration.has_environment(configuration.ENVIRONMENT):
        _ipython_prompt = configuration.read(option="ipython_prompt")
        if _ipython_prompt in [None, "True"]:
            config.session.ipython_prompt = True
        else:
            config.session.ipython_prompt = False
    else:
        config.session.ipython_prompt = True
        configuration.write(option="ipython_prompt", value="True")
