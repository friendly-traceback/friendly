from .main import *  # noqa
from .main import install
from friendly import settings

settings.ENVIRONMENT = "IDLE"

__all__ = list(helpers)  # noqa
__all__.append("run")  # noqa
__all__.append("start_console")  # noqa
__all__.append("Friendly")  # noqa
install()
