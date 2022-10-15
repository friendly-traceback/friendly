import friendly
from .main import *  # noqa
from .main import install
from friendly import settings
from friendly_traceback.console_helpers import friendly_tb
from friendly_traceback import config, add_ignored_warnings

settings.ENVIRONMENT = "IDLE"


def do_not_show_warnings(warning_instance, warning_type, filename, lineno):
    # These warnings occur with friendly_idle
    return warning_type == ImportWarning and str(warning_instance) in {
        "PatchingFinder.find_spec() not found; falling back to find_module()",
        "PatchingLoader.exec_module() not found; falling back to load_module()",
    }


add_ignored_warnings(do_not_show_warnings)

__all__ = list(helpers)  # noqa
__all__.extend(("run", "start_console", "Friendly"))
__all__.remove("disable")
__all__.remove("enable")
install()

if config.did_exception_occur_before():
    friendly.print_repl_header()
    friendly_tb()  # noqa
