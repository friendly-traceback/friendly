"""
formatters.py
==============

This module currently contains 4 formatters

* ``jupyter()``: experimental formatter for Jupyter notebooks

* ``markdown()``: This produces an output formatted with markdown syntax.

* ``markdown_docs()``: This produces an output formatted markdown syntax,
    but where each header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial top headers.

* ``rich_markdown()``: This produces an output formatted with markdown syntax,
    with some modification, with the end result intended to be printed
    in colour in a console using Rich (https://github.com/willmcgugan/rich).
"""
from .my_gettext import current_lang
from friendly_traceback.base_formatters import no_result, select_items, repl
from friendly_traceback.config import session
from friendly import theme

from pygments import highlight  # noqa
from pygments.lexers import PythonLexer, PythonTracebackLexer  # noqa
from pygments.formatters import HtmlFormatter  # noqa


ipython_available = False
try:  # pragma: no cover

    from IPython.display import display, HTML  # noqa

    ipython_available = True
except ImportError:
    display = HTML = lambda x: x

RICH_HEADER = False


def rich_writer(text):  # pragma: no cover
    """Default writer"""
    global RICH_HEADER

    if session.rich_add_vspace:
        session.console.print()
    md = theme.friendly_rich.Markdown(
        text, inline_code_lexer="python", code_theme=theme.CURRENT_THEME
    )
    if RICH_HEADER:
        title = "Traceback"
        md = theme.friendly_rich.Panel(md, title=title)
        RICH_HEADER = False
    session.console.print(md)


def html_escape(text):  # pragma: no cover
    text = (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n\n", "<br>")
    )
    while "`" in text:
        text = text.replace("`", "<code>", 1)
        text = text.replace("`", "</code>", 1)
    return text


# For some reason, moving this to friendly.ipython
# and trying to import it from there uninstalls everything: it is as though
# it starts a new iPython subprocess.
def jupyter(info, include="friendly_tb"):  # pragma: no cover
    """Jupyter formatter using pygments and html format."""
    _ = current_lang.translate
    css = HtmlFormatter().get_style_defs(".highlight")
    display(HTML(f"<style>{css}</style>"))  # noqa
    items_to_show = select_items(include)
    result = False
    for item in items_to_show:
        if item in info:
            result = True
            if "source" in item or "variable" in item:
                text = info[item]
                text = highlight(text, PythonLexer(), HtmlFormatter())
                display(HTML(text))
            elif "traceback" in item:
                text = info[item]
                text = highlight(text, PythonTracebackLexer(), HtmlFormatter())
                display(HTML(text))
            elif item == "message":  # format like last line of traceback
                content = info[item].split(":")
                error_name = content[0]
                message = ":".join(content[1:]) if len(content) > 1 else ""
                text = "".join(
                    [
                        '<div class="highlight"><pre><span class="gr">',
                        error_name,
                        '</span>: <span class="n">',
                        message,
                        "</span></pre></div>",
                    ]
                )
                display(HTML(text))
            elif item == "suggest":
                text = html_escape(info[item])
                display(HTML(f"<p><i>{text}<i><p>"))
            else:
                text = html_escape(info[item])
                if "header" in item:
                    display(HTML(f"<p><b>{text}</b></p>"))
                else:
                    display(HTML(f'<p style="width: 70ch">{text}</p>'))
    if not result:
        text = no_result(info, include)
        if text:
            display(HTML(f'<p style="width: 70ch;">{text}</p>'))
    return ""


if not ipython_available:
    jupyter = repl  # noqa


def markdown(info, include="friendly_tb"):  # pragma: no cover
    """Traceback formatted with markdown syntax.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.
    """
    return _markdown(info, include)


def markdown_docs(info, include="explain"):  # pragma: no cover
    """Traceback formatted with markdown syntax, where each
    header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial
    top headers.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    is further processed.
    """
    return _markdown(info, include, documentation=True)


def rich_markdown(info, include="friendly_tb"):  # pragma: no cover
    """Traceback formatted with with markdown syntax suitable for
    printing in color in the console using Rich.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.

    Some additional processing is done just prior to doing the
    final output, by ``session._write_err()``.
    """
    return _markdown(info, include, rich=True)


def _markdown(info, include, rich=False, documentation=False):  # pragma: no cover
    """Traceback formatted with with markdown syntax."""
    global RICH_HEADER
    RICH_HEADER = False

    markdown_items = {
        "header": ("# ", ""),
        "message": ("", ""),
        "suggest": ("", "\n"),
        "generic": ("", ""),
        "parsing_error": ("", ""),
        "parsing_error_source": ("```python\n", "\n```"),
        "cause": ("", ""),
        "last_call_header": ("## ", ""),
        "last_call_source": ("```python\n", "\n```"),
        "last_call_variables": ("```python\n", "\n```"),
        "exception_raised_header": ("## ", ""),
        "exception_raised_source": ("```python\n", "\n```"),
        "exception_raised_variables": ("```python\n", "\n```"),
        "simulated_python_traceback": ("```pytb\n", "\n```"),
        "original_python_traceback": ("```pytb\n", "\n```"),
        "shortened_traceback": ("```pytb\n", "\n```"),
    }

    items_to_show = select_items(include)  # tb_items_to_show(level=level)
    if rich and include == "explain":
        RICH_HEADER = True  # Skip it here; handled by session.py
    result = [""]
    for item in items_to_show:
        if item in info and info[item].strip():
            # With normal markdown formatting, it does not make sense to have a
            # header end with a colon.
            # However, we style headers differently with Rich; see
            # Rich theme in file friendly_rich.
            content = info[item]
            if item.endswith("header"):
                content = content.rstrip(":")
            if item == "message" and rich:
                # Ensure that the exception name is highlighted.
                content = content.split(":")
                content[0] = "`" + content[0] + "`"
                content = ":".join(content)

            prefix, suffix = markdown_items[item]
            if documentation and prefix.startswith("#"):
                prefix = "##" + prefix
            result.append(prefix + content + suffix)

    if result == [""]:
        return no_result(info, include)

    if include == "message":
        return result[1]

    return "\n\n".join(result)
