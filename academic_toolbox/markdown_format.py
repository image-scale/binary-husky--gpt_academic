"""
Markdown formatting module.
Provides markdown-to-HTML conversion with code highlighting and LaTeX math support.
"""
import re
import math
import markdown
from functools import lru_cache

try:
    from latex2mathml.converter import convert as tex2mathml
    LATEX2MATHML_AVAILABLE = True
except ImportError:
    LATEX2MATHML_AVAILABLE = False
    def tex2mathml(content, *args, **kwargs):
        return f"<span class='math'>{content}</span>"


# Math pattern definitions
MATH_PATTERNS = {
    r"(?<!\\|\$)(\$)([^\$]+)(\$)": {"allow_multi_lines": False},  # $...$
    r"(?<!\\)(\$\$)([^\$]+)(\$\$)": {"allow_multi_lines": True},   # $$...$$
    r"(?<!\\)(\\\[)(.+?)(\\\])": {"allow_multi_lines": False},     # \[...\]
    r'(?<!\\)(\\\()(.+?)(\\\))': {'allow_multi_lines': False},     # \(...\)
}


def tex2mathml_safe(content, *args, **kwargs):
    """
    Safely convert LaTeX to MathML, catching any exceptions.

    Args:
        content: LaTeX string to convert
        *args, **kwargs: Additional arguments for tex2mathml

    Returns:
        MathML string or original content if conversion fails
    """
    try:
        return tex2mathml(content, *args, **kwargs)
    except Exception:
        return f"<span class='math'>{content}</span>"


def is_equation(text):
    """
    Check if text contains LaTeX equations.

    Args:
        text: The text to check

    Returns:
        True if text contains math formulas
    """
    if not text or not isinstance(text, str):
        return False

    if "```" in text and "```reference" not in text:
        return False

    if "$" not in text and "\\[" not in text:
        return False

    matches = []
    for pattern, props in MATH_PATTERNS.items():
        flags = re.ASCII | re.DOTALL if props["allow_multi_lines"] else re.ASCII
        matches.extend(re.findall(pattern, text, flags))

    if len(matches) == 0:
        return False

    illegal_pattern = re.compile(r"[^\x00-\x7F]|echo")
    for match in matches:
        if len(match) != 3:
            continue
        eq_candidate = match[1]
        if not illegal_pattern.search(eq_candidate):
            return True

    return False


def fix_markdown_indent(text):
    """
    Fix non-standard markdown list indentation.

    Args:
        text: Markdown text to fix

    Returns:
        Text with fixed indentation
    """
    if not text or not isinstance(text, str):
        return text

    if (" - " not in text) or (". " not in text):
        return text

    lines = text.split("\n")
    pattern = re.compile(r"^\s+-")
    activated = False

    for i, line in enumerate(lines):
        if line.startswith("- ") or line.startswith("1. "):
            activated = True
        if activated and pattern.match(line):
            stripped_string = line.lstrip()
            num_spaces = len(line) - len(stripped_string)
            if (num_spaces % 4) == 3:
                num_spaces_should_be = math.ceil(num_spaces / 4) * 4
                lines[i] = " " * num_spaces_should_be + stripped_string

    return "\n".join(lines)


def close_up_code_segment(text):
    """
    Close unclosed code blocks in streaming output.

    Args:
        text: Text that might have unclosed code blocks

    Returns:
        Text with code blocks properly closed
    """
    if not text or "```" not in text:
        return text

    if text.endswith("```"):
        return text

    segments = text.split("```")
    n_mark = len(segments) - 1

    if n_mark % 2 == 1:
        return text + "\n```"

    return text


def _replace_math_render(match):
    """Replace math match with rendered MathML."""
    content = match.group(1)
    if "mode=display" in match.group(0):
        if "\\begin{aligned}" in content:
            content = content.replace("\\begin{aligned}", "\\begin{array}")
            content = content.replace("\\end{aligned}", "\\end{array}")
            content = content.replace("&", " ")
        return tex2mathml_safe(content, display="block")
    else:
        return tex2mathml_safe(content)


def _replace_math_no_render(match):
    """Replace math with colored display (for copy/paste)."""
    content = match.group(1)
    if "mode=display" in match.group(0):
        content = content.replace("\n", "</br>")
        return f'<font color="#00FF00">$$</font><font color="#FF00FF">{content}</font><font color="#00FF00">$$</font>'
    else:
        return f'<font color="#00FF00">$</font><font color="#FF00FF">{content}</font><font color="#00FF00">$</font>'


@lru_cache(maxsize=128)
def markdown_to_html(text):
    """
    Convert markdown text to HTML with code highlighting and math support.

    Args:
        text: Markdown text to convert

    Returns:
        HTML string
    """
    if not text or not isinstance(text, str):
        return text or ""

    pre = '<div class="markdown-body">'
    suf = "</div>"

    if text.startswith(pre) and text.endswith(suf):
        return text

    text = fix_markdown_indent(text)

    extensions = [
        "sane_lists",
        "tables",
        "fenced_code",
        "codehilite",
    ]

    extension_configs = {
        "codehilite": {
            "css_class": "codehilite",
            "guess_lang": True,
        },
    }

    if is_equation(text):
        try:
            extensions.append("mdx_math")
            extension_configs["mdx_math"] = {
                "enable_dollar_delimiter": True,
                "use_gitlab_delimiters": False,
            }

            html = markdown.markdown(
                text=text,
                extensions=extensions,
                extension_configs=extension_configs,
            )

            find_pattern = r'<script type="math/tex(?:.*?)>(.*?)</script>'

            html_copy = re.sub(
                find_pattern,
                _replace_math_no_render,
                html,
                flags=re.DOTALL,
            )

            html_render = re.sub(
                find_pattern,
                _replace_math_render,
                html,
                flags=re.DOTALL,
            )

            split = markdown.markdown(text="---")
            return pre + html_copy + split + html_render + suf

        except Exception:
            pass

    html = markdown.markdown(
        text=text,
        extensions=extensions,
        extension_configs=extension_configs,
    )

    return pre + html + suf


def simple_markdown_to_html(text):
    """
    Simple markdown to HTML conversion without math processing.

    Args:
        text: Markdown text to convert

    Returns:
        HTML string
    """
    if not text or not isinstance(text, str):
        return text or ""

    pre = '<div class="markdown-body">'
    suf = "</div>"

    if text.startswith(pre) and text.endswith(suf):
        return text

    html = markdown.markdown(
        text,
        extensions=["fenced_code", "codehilite", "tables", "sane_lists"],
        extension_configs={
            "codehilite": {
                "css_class": "codehilite",
                "guess_lang": True,
            },
        },
    )

    return pre + html + suf


def format_chat_output(query, response):
    """
    Format chat query and response for display.

    Args:
        query: User's input
        response: Model's response

    Returns:
        Tuple of (formatted_query, formatted_response)
    """
    if response is not None:
        response = close_up_code_segment(response)

    formatted_query = simple_markdown_to_html(query) if query else None
    formatted_response = markdown_to_html(response) if response else None

    return formatted_query, formatted_response
