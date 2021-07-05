"""
This is a proof of concept of some preliminary work related
to https://bugs.python.org/issue43476


"""


import sys
from friendly_traceback.my_gettext import current_lang
from friendly_traceback.config import session

from .main import idle_writer


if sys.version_info >= (3, 10):  # current hack

    class FakeSyntaxError:
        def __init__(self, value):
            self.msg = value[0]
            self.filename = value[1]
            self.lineno = int(value[2])
            self.offset = int(value[3])
            self.text = value[4]
            self.end_lineno = int(value[5])
            self.end_offset = int(value[6])

        def __str__(self):
            return self.msg

    def friendly_syntax_error():
        _ = current_lang.translate
        filename = "<SyntaxError>"
        rpchandler = rpc.objecttable["exec"].rpchandler  # noqa
        try:
            lines = rpchandler.remotecall("linecache", "getlines", (filename, None), {})
        except Exception:  # noqa
            idle_writer((_("No SyntaxError recorded."), "stderr"))
            return None
        if not lines:
            idle_writer((_("No SyntaxError recorded."), "stderr"))
            return
        exc_name, *args = eval(lines[0])
        value = FakeSyntaxError(args[0])
        if " indent" in exc_name or " unindent" in exc_name:
            exc_name = "IndentationError"
        exc_type = eval(exc_name)

        include = get_include()  # noqa
        set_include("explain")  # noqa
        session.exception_hook(exc_type, value, "")
        set_include(include)  # noqa

    _old_explain = explain  # noqa

    def explain(include="explain"):
        _ = current_lang.translate
        if include == "syntax":
            idle_writer((_("Not yet implemented."), "stderr"))
            # friendly_syntax_error()
        else:
            _old_explain(include=include)
