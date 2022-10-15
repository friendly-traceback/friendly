import friendly
import friendly_traceback
from friendly_traceback.config import session


def test_basic():
    friendly.set_formatter("dark", color_system="truecolor")
    console = session.console
    with console.capture() as capture:
        try:
            a = b
        except NameError:
            friendly_traceback.explain_traceback()
    str_output = capture.get()
    with open("tests/basic_text.out",encoding="utf8") as f:
        result = f.read()
    assert str_output == result
