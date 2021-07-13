# Monkeypatching the traceback lexer so that it treats
# "Code block" the same as "File"
from pygments.lexers.python import PythonTracebackLexer
from pygments.lexer import bygroups
from pygments.token import Text, Name, Number, Operator, Generic


PythonTracebackLexer.tokens["root"].insert(
    0,
    # SyntaxError in interactive interpreter can start with this.
    (r"^(?=  Code block \[\d+\], line \d+)", Generic.Traceback, "intb"),
)

PythonTracebackLexer.tokens["intb"].insert(
    0,
    (
        r"^(  Code block )(\[)(\d+)(\])(, line )(\d+)(, in )(.+)(\n)",
        bygroups(Text, Operator, Number, Operator, Text, Number, Text, Name, Text),
    ),
)
PythonTracebackLexer.tokens["intb"].insert(
    1,
    (
        r"^(  Code block )(\[)(\d+)(\])(, line )(\d+)(\n)",
        bygroups(Text, Operator, Number, Operator, Text, Number, Text),
    ),
)
