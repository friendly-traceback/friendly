"""
formatters.py
==============

This module currently contains the following formatters

* ``jupyter_interactive()``: formatter for jupyter notebooks that uses
    buttons to show and hide parts of the information instead of
    having to type them as functions to be executed.

* ``jupyter()``: basic formatter for Jupyter notebooks

* ``markdown()``: This produces an output formatted with Markdown syntax.

* ``markdown_docs()``: This produces an output formatted Markdown syntax,
    but where each header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial top headers.

* ``rich_markdown()``: This produces an output formatted with Markdown syntax,
    with some modification, with the end result intended to be printed
    in colour in a console using Rich (https://github.com/willmcgugan/rich).
"""
from .my_gettext import current_lang
from friendly_traceback.base_formatters import no_result, repl, select_items
from friendly_traceback.config import session
from friendly_traceback.typing_info import InclusionChoice, Info
from friendly.theme import friendly_pygments

from pygments import highlight  # noqa
from pygments.lexers import PythonLexer, PythonTracebackLexer  # noqa
from pygments.formatters import HtmlFormatter  # noqa

from rich import jupyter as rich_jupyter
from rich.markdown import Markdown
from rich.panel import Panel

ipython_available = False
try:  # pragma: no cover

    from IPython.display import display, HTML  # noqa

    ipython_available = True
except ImportError:
    display = HTML = lambda x: x

RICH_HEADER = False  # not a constant
WIDE_OUTPUT = False  # not a constant
COUNT = 0  # not a constant


def jupyter_interactive(
    info: Info, include: InclusionChoice = "friendly_tb"
) -> None:  # noqa
    """This implements a formatter that inserts buttons in a jupyter notebook
    allowing to selectively show what/why/where, instead of
    showing the friendly_tb by default."""
    global COUNT
    if include != "friendly_tb":
        text = _markdown(info, include=include, rich=True)
        rich_writer(text)
        return
    COUNT += 1
    _ = current_lang.translate
    session.rich_add_vspace = False
    add_message(info, count=COUNT)
    if "detailed_tb" in info:
        add_detailed_tb = len(info["detailed_tb"]) > 2
    else:
        add_detailed_tb = False
    add_control(count=COUNT, add_detailed_tb=add_detailed_tb)
    add_friendly_tb(info, count=COUNT)
    add_interactive_item(info, "what", count=COUNT)
    add_interactive_item(info, "why", count=COUNT)
    add_interactive_item(info, "where", count=COUNT)
    if add_detailed_tb:
        add_interactive_item(info, "detailed_tb", count=COUNT)


def add_message(info: Info, count: int = -1) -> None:
    """Shows the error message. By default, this is the only item shown
    other than a button to reveal"""
    old_jupyter_html_format = rich_jupyter.JUPYTER_HTML_FORMAT
    rich_jupyter.JUPYTER_HTML_FORMAT = (
        "<div id='friendly-message{count}'>".format(count=count)
        + old_jupyter_html_format
        + "</div>"
    )
    text = _markdown(info, include="message", rich=True)
    rich_writer(text)
    rich_jupyter.JUPYTER_HTML_FORMAT = old_jupyter_html_format


def add_friendly_tb(info: Info, count: int = -1) -> None:
    """Adds the friendly_tb, hidden by default"""
    old_jupyter_html_format = rich_jupyter.JUPYTER_HTML_FORMAT
    name = "friendly_tb"
    rich_jupyter.JUPYTER_HTML_FORMAT = (
        "<div id='friendly-tb-{name}-content{count}' style='display:none'>".format(
            name=name, count=count
        )
        + old_jupyter_html_format
        + "</div>"
    )
    text = _markdown(info, include="friendly_tb", rich=True)
    rich_writer(text)
    rich_jupyter.JUPYTER_HTML_FORMAT = old_jupyter_html_format


def add_interactive_item(info: Info, name: InclusionChoice, count: int = -1) -> None:
    """Adds interactive items (what/why/where) with buttons to toggle
    their visibility."""
    _ = current_lang.translate
    old_jupyter_html_format = rich_jupyter.JUPYTER_HTML_FORMAT

    content = """<script type="text/Javascript"> function toggle_{name}{count}(){{
     var content = document.getElementById('friendly-tb-{name}-content{count}');
     var btn = document.getElementById('friendly-tb-btn-show-{name}{count}');
        if (content.style.display === 'none') {{
            content.style.display = 'block';
            btn.textContent = "{hide} {name}()";
        }} else {{
            content.style.display = 'none';
            btn.textContent = "{name}()";
       }}
    }}
     </script>
     <button
         id='friendly-tb-btn-show-{name}{count}'
         onclick='toggle_{name}{count}()'
         style='display:none {btn_style}'>
     {name}()
     </button>
    """.format(
        name=name, count=count, hide=_("Hide"), btn_style=session.jupyter_button_style
    )
    display(HTML(content))

    rich_jupyter.JUPYTER_HTML_FORMAT = (
        "<div id='friendly-tb-{name}-content{count}' style='display:none'>".format(
            name=name, count=count
        )
        + old_jupyter_html_format
        + "</div>"
    )
    text = _markdown(info, include=name, rich=True)
    rich_writer(text)

    rich_jupyter.JUPYTER_HTML_FORMAT = old_jupyter_html_format


def add_control(count: int = -1, add_detailed_tb: bool = False) -> None:
    """Adds a single button to control the visibility of all other elements."""
    _ = current_lang.translate
    if add_detailed_tb:
        btn_detailed_tb = """;var btn_detailed_tb =
        document.getElementById('friendly-tb-btn-show-detailed_tb{count}');""".format(
            count=count
        )
        var_detailed_tb_content = """var detailed_tb_content =
        document.getElementById('friendly-tb-detailed_tb-content{count}');""".format(
            count=count
        )
        show_detailed_tb_button = """btn_detailed_tb.style.display = 'block';"""
        hide_detailed_tb_button = """
            btn_detailed_tb.style.display = 'none';
            btn_detailed_tb.textContent = 'detailed_tb()';"""
        show_detailed_tb_content = "detailed_tb_content.display = 'block';"
        hide_detailed_tb_content = "detailed_tb_content.display = 'none';"
    else:
        btn_detailed_tb = ""
        var_detailed_tb_content = ""
        show_detailed_tb_button = ""
        hide_detailed_tb_button = ""
        show_detailed_tb_content = ""
        hide_detailed_tb_content = ""
    content = """
        <button
            id='friendly-tb-btn-show{count}'
            onclick='friendly_toggle_more{count}()'
            style='{btn_style}'>
        {more}
        </button>
        <script type="text/Javascript"> function friendly_toggle_more{count}(){{
        var btn = document.getElementById('friendly-tb-btn-show{count}');
        var btn_what = document.getElementById('friendly-tb-btn-show-what{count}');
        var btn_where = document.getElementById('friendly-tb-btn-show-where{count}');
        var btn_why = document.getElementById('friendly-tb-btn-show-why{count}');
        {btn_detailed_tb};
        var message = document.getElementById('friendly-message{count}');
        var friendly_tb_content = document.getElementById('friendly-tb-friendly_tb-content{count}');
        var what_content = document.getElementById('friendly-tb-what-content{count}');
        var why_content = document.getElementById('friendly-tb-why-content{count}');
        var where_content = document.getElementById('friendly-tb-where-content{count}');
        {var_detailed_tb_content};

        if (btn_what.style.display == 'none'){{
            message.style.display = 'none';
            btn_what.style.display = 'block';
            btn_why.style.display = 'block';
            btn_where.style.display = 'block';
            friendly_tb_content.style.display = 'block';
            {show_detailed_tb_content};
            btn.textContent = "{only}";
            {show_detailed_tb_button};
        }} else {{
            btn_what.style.display = 'none';
            btn_what.textContent = 'what()';
            btn_why.style.display = 'none';
            btn_why.textContent = 'why()';
            btn_where.style.display = 'none';
            btn_where.textContent = 'where()';
            what_content.style.display = 'none';
            why_content.style.display = 'none';
            where_content.style.display = 'none';
            {hide_detailed_tb_content};
            friendly_tb_content.style.display = 'none';
            message.style.display = 'block';
            btn.textContent = "{more}";
            {hide_detailed_tb_button};
        }}
        }};
        </script>
        """.format(
        count=count,
        more=_("More ..."),
        only=_("Show message only"),
        btn_style=session.jupyter_button_style,
        btn_detailed_tb=btn_detailed_tb,
        var_detailed_tb_content=var_detailed_tb_content,
        show_detailed_tb_content=show_detailed_tb_content,
        hide_detailed_tb_content=hide_detailed_tb_content,
        show_detailed_tb_button=show_detailed_tb_button,
        hide_detailed_tb_button=hide_detailed_tb_button,
    )
    display(HTML(content))


def rich_writer(text: str) -> None:  # pragma: no cover
    """Default writer"""
    global RICH_HEADER, WIDE_OUTPUT
    if session.rich_add_vspace:
        session.console.print()
    md = Markdown(
        text, inline_code_lexer="python", code_theme=friendly_pygments.CURRENT_THEME
    )
    if RICH_HEADER:
        title = "Traceback"
        md = Panel(md, title=title)
        RICH_HEADER = False
    session.console.print(md)
    if WIDE_OUTPUT:
        session.console.width = session.rich_width
        WIDE_OUTPUT = False


def html_escape(text: str) -> str:  # pragma: no cover
    if not text:
        return ""
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
def jupyter(
    info: Info, include: InclusionChoice = "friendly_tb"
) -> str:  # pragma: no cover
    """Jupyter formatter using pygments and html format.

    This can be used as a jupyter theme agnostic formatter as it
    works equally well with a light or dark theme.
    However, some information shown may be less than optimal
    when it comes to visibility/contrast.
    """
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
            elif "message" in item:  # format like last line of traceback
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
                display(HTML(f"<p><i>{text}</i></p>"))
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


def markdown(
    info: Info, include: InclusionChoice = "friendly_tb"
) -> str:  # pragma: no cover
    """Traceback formatted with Markdown syntax.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.
    """
    return _markdown(info, include)


def markdown_docs(
    info: Info, include: InclusionChoice = "explain"
) -> str:  # pragma: no cover
    """Traceback formatted with Markdown syntax, where each
    header is shifted down by 2 (h1 -> h3, etc.) so that they
    can be inserted in a document, without creating artificial
    top headers.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    is further processed.
    """
    return _markdown(info, include, documentation=True)


def rich_markdown(
    info: Info, include: InclusionChoice = "friendly_tb"
) -> str:  # pragma: no cover
    """Traceback formatted with Markdown syntax suitable for
    printing in color in the console using Rich.

    Some minor changes of the traceback info content are done,
    for nicer final display when the markdown generated content
    if further processed.

    Some additional processing is done just prior to doing the
    final output, by ``session._write_err()``.
    """
    return _markdown(info, include, rich=True)


def detailed_tb(info: Info) -> str:  # Special case
    # TODO: document this
    if "detailed_tb" not in info:
        return ""
    markdown_items = {
        "source": ("```python\n", "\n```"),
        "var_info": ("```python\n", "\n```"),
    }
    result = [""]
    for location, source, var_info in info["detailed_tb"]:
        result.append(location)
        prefix, suffix = markdown_items["source"]
        result.append(prefix + source + suffix)
        if var_info:
            prefix, suffix = markdown_items["var_info"]
            result.append(prefix + var_info + suffix)
        result.append("\n")
    return "\n".join(result)


def _markdown(
    info: Info,
    include: InclusionChoice,
    rich: bool = False,
    documentation: bool = False,
) -> str:  # pragma: no cover
    """Traceback formatted with Markdown syntax."""
    global RICH_HEADER, WIDE_OUTPUT
    if include == "detailed_tb" and "detailed_tb" in info:
        return detailed_tb(info)
    elif include == "detailed_tb":
        return ""
    if (
        rich
        and session.is_jupyter
        and session.rich_tb_width is not None
        and session.rich_tb_width != session.rich_width
        and include in ["friendly_tb", "python_tb", "debug_tb", "where", "explain"]
    ):
        session.console.width = session.rich_tb_width
        WIDE_OUTPUT = True
    markdown_items = {
        "header": ("# ", ""),
        "message": ("", ""),
        "suggest": ("", "\n"),
        "warning message": ("`", "`\n"),
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
        "warning location header": ("#### ", ""),
        "warning source": ("```python\n", "\n```"),
        "warning variables": ("```python\n", "\n```"),
        "additional variable warning": ("#### ", ""),
    }

    items_to_show = select_items(include)  # tb_items_to_show(level=level)
    if rich and include == "explain":
        RICH_HEADER = True  # Skip it here; handled by session.py
    result = [""]
    for item in items_to_show:
        if item in info and info[item].strip():
            # With normal Markdown formatting, it does not make sense to have a
            # header end with a colon.
            # However, we style headers differently with Rich; see
            # Rich theme in file friendly_rich.
            content = info[item]
            if item.endswith("header"):
                content = (
                    content.rstrip(":")
                    .replace("' ", "'` ")
                    .replace(" '", " `'")
                    .replace("'.", "'`.")
                )
            if item == "message" and rich:
                # Ensure that the exception name is highlighted.
                content = content.split(":")
                content[0] = "`" + content[0] + "`"
                content = ":".join(content)

            if "header" in item and "[" in content:
                content = content.replace("[", "`[").replace("]", "]`")

            if item == "parsing_error" and "[" in content:
                content = content.replace("[", "`[").replace("]", "]`")

            prefix, suffix = markdown_items[item]
            if documentation and prefix.startswith("#"):
                prefix = "##" + prefix
            result.append(prefix + content + suffix)

    if result == [""]:
        return no_result(info, include)

    if include == "message":
        return result[1]

    return "\n\n".join(result)
