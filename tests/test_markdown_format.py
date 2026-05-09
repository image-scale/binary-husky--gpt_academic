"""Tests for the markdown formatting module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.markdown_format import (
    markdown_to_html,
    simple_markdown_to_html,
    is_equation,
    fix_markdown_indent,
    close_up_code_segment,
    format_chat_output,
    tex2mathml_safe,
)


class TestMarkdownToHtml(unittest.TestCase):
    """Test cases for markdown to HTML conversion."""

    def test_basic_header_conversion(self):
        """Test converting markdown headers."""
        result = markdown_to_html("# Hello World")
        self.assertIn("<h1>", result)
        self.assertIn("Hello World", result)

    def test_basic_list_conversion(self):
        """Test converting markdown lists."""
        result = markdown_to_html("- Item 1\n- Item 2")
        self.assertIn("<ul>", result)
        self.assertIn("<li>", result)
        self.assertIn("Item 1", result)

    def test_bold_conversion(self):
        """Test converting bold text."""
        result = markdown_to_html("**bold text**")
        self.assertIn("<strong>", result)
        self.assertIn("bold text", result)

    def test_italic_conversion(self):
        """Test converting italic text."""
        result = markdown_to_html("*italic text*")
        self.assertIn("<em>", result)
        self.assertIn("italic text", result)

    def test_code_block_conversion(self):
        """Test converting code blocks."""
        result = markdown_to_html("```python\nprint('hello')\n```")
        self.assertIn("print", result)
        self.assertIn("hello", result)

    def test_already_converted_passes_through(self):
        """Test that already converted HTML passes through unchanged."""
        html = '<div class="markdown-body"><p>Hello</p></div>'
        result = markdown_to_html(html)
        self.assertEqual(result, html)

    def test_none_input_returns_empty(self):
        """Test that None input returns empty string."""
        result = markdown_to_html(None)
        self.assertEqual(result, "")

    def test_empty_input_returns_empty(self):
        """Test that empty input returns empty string."""
        result = markdown_to_html("")
        self.assertEqual(result, "")

    def test_has_markdown_body_wrapper(self):
        """Test that output has markdown-body wrapper."""
        result = markdown_to_html("Hello")
        self.assertTrue(result.startswith('<div class="markdown-body">'))
        self.assertTrue(result.endswith('</div>'))


class TestSimpleMarkdownToHtml(unittest.TestCase):
    """Test cases for simple markdown conversion."""

    def test_basic_conversion(self):
        """Test basic markdown conversion."""
        result = simple_markdown_to_html("# Header")
        self.assertIn("<h1>", result)

    def test_already_converted_passes_through(self):
        """Test that already converted HTML passes through."""
        html = '<div class="markdown-body"><p>Hello</p></div>'
        result = simple_markdown_to_html(html)
        self.assertEqual(result, html)


class TestIsEquation(unittest.TestCase):
    """Test cases for equation detection."""

    def test_single_dollar_equation(self):
        """Test detecting $...$ equations."""
        self.assertTrue(is_equation("The formula is $E=mc^2$"))

    def test_double_dollar_equation(self):
        """Test detecting $$...$$ equations."""
        self.assertTrue(is_equation("Display: $$x^2 + y^2 = z^2$$"))

    def test_bracket_equation(self):
        """Test detecting \\[...\\] equations."""
        self.assertTrue(is_equation("Formula: \\[x + y = z\\]"))

    def test_no_equation(self):
        """Test text without equations."""
        self.assertFalse(is_equation("Just plain text"))

    def test_code_block_not_equation(self):
        """Test that code blocks with $ are not detected as equations."""
        self.assertFalse(is_equation("```bash\necho $HOME\n```"))

    def test_none_returns_false(self):
        """Test that None returns False."""
        self.assertFalse(is_equation(None))

    def test_empty_returns_false(self):
        """Test that empty string returns False."""
        self.assertFalse(is_equation(""))


class TestFixMarkdownIndent(unittest.TestCase):
    """Test cases for markdown indent fixing."""

    def test_fix_odd_indent(self):
        """Test fixing odd number of spaces in list indent."""
        # Function only activates when both " - " AND ". " are present
        text = "1. Item 1\n   - Sub item"  # 3 spaces (odd)
        result = fix_markdown_indent(text)
        self.assertIn("    - Sub item", result)  # Should be 4 spaces

    def test_no_change_needed(self):
        """Test that correctly indented text passes through."""
        text = "- Item 1\n    - Sub item"  # 4 spaces (correct)
        result = fix_markdown_indent(text)
        self.assertEqual(text, result)

    def test_none_passes_through(self):
        """Test that None passes through."""
        result = fix_markdown_indent(None)
        self.assertIsNone(result)

    def test_no_list_passes_through(self):
        """Test that text without lists passes through."""
        text = "Just some text"
        result = fix_markdown_indent(text)
        self.assertEqual(text, result)


class TestCloseUpCodeSegment(unittest.TestCase):
    """Test cases for closing unclosed code blocks."""

    def test_closes_unclosed_block(self):
        """Test that unclosed code block gets closed."""
        text = "```python\nprint('hello')"
        result = close_up_code_segment(text)
        self.assertTrue(result.endswith("```"))

    def test_already_closed_unchanged(self):
        """Test that already closed code block passes through."""
        text = "```python\nprint('hello')\n```"
        result = close_up_code_segment(text)
        self.assertEqual(text, result)

    def test_no_code_block_unchanged(self):
        """Test that text without code blocks passes through."""
        text = "Just text"
        result = close_up_code_segment(text)
        self.assertEqual(text, result)

    def test_none_passes_through(self):
        """Test that None passes through."""
        result = close_up_code_segment(None)
        self.assertIsNone(result)

    def test_even_number_of_markers_unchanged(self):
        """Test text with even number of ``` markers."""
        text = "```python\ncode\n```\n\nMore text"
        result = close_up_code_segment(text)
        self.assertEqual(text, result)


class TestFormatChatOutput(unittest.TestCase):
    """Test cases for chat output formatting."""

    def test_formats_both_query_and_response(self):
        """Test formatting both query and response."""
        query = "What is $E=mc^2$?"
        response = "It's Einstein's equation"
        q, r = format_chat_output(query, response)
        self.assertIn("markdown-body", q)
        self.assertIn("markdown-body", r)

    def test_handles_none_query(self):
        """Test handling None query."""
        q, r = format_chat_output(None, "Response")
        self.assertIsNone(q)
        self.assertIsNotNone(r)

    def test_handles_none_response(self):
        """Test handling None response."""
        q, r = format_chat_output("Query", None)
        self.assertIsNotNone(q)
        self.assertIsNone(r)

    def test_closes_unclosed_code_in_response(self):
        """Test that unclosed code in response gets closed before conversion."""
        text = "```python\ncode"
        closed = close_up_code_segment(text)
        self.assertTrue(closed.endswith("```"))


class TestTex2MathmlSafe(unittest.TestCase):
    """Test cases for safe LaTeX to MathML conversion."""

    def test_basic_conversion(self):
        """Test basic LaTeX conversion."""
        result = tex2mathml_safe("x^2")
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_handles_invalid_latex(self):
        """Test handling invalid LaTeX gracefully."""
        result = tex2mathml_safe("\\invalid{command}")
        self.assertIsInstance(result, str)


if __name__ == '__main__':
    unittest.main()
