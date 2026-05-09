"""Tests for the colorful logging utilities module."""
import os
import sys
import unittest
from io import StringIO

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.colorful import (
    log_red,
    log_green,
    log_blue,
    log_yellow,
    log_cyan,
    log_magenta,
    log_white,
    is_colorama_available,
    _format_message,
)


class TestFormatMessage(unittest.TestCase):
    """Test cases for message formatting."""

    def test_single_string_argument(self):
        """Test formatting single string argument."""
        result = _format_message("hello")
        self.assertEqual(result, "hello")

    def test_multiple_string_arguments(self):
        """Test formatting multiple string arguments."""
        result = _format_message("hello", "world")
        self.assertEqual(result, "hello world")

    def test_non_string_arguments(self):
        """Test formatting non-string arguments."""
        result = _format_message("count:", 42)
        self.assertEqual(result, "count: 42")

    def test_mixed_arguments(self):
        """Test formatting mixed argument types."""
        result = _format_message("value", 3.14, True, None)
        self.assertEqual(result, "value 3.14 True None")

    def test_empty_arguments(self):
        """Test formatting with no arguments."""
        result = _format_message()
        self.assertEqual(result, "")


class TestLogColors(unittest.TestCase):
    """Test cases for colored log functions."""

    def setUp(self):
        """Redirect stdout for testing."""
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        """Restore stdout."""
        sys.stdout = self.original_stdout

    def test_log_red_contains_message(self):
        """Test that log_red outputs the message."""
        log_red("error message")
        output = self.held_output.getvalue()
        self.assertIn("error message", output)

    def test_log_green_contains_message(self):
        """Test that log_green outputs the message."""
        log_green("success message")
        output = self.held_output.getvalue()
        self.assertIn("success message", output)

    def test_log_blue_contains_message(self):
        """Test that log_blue outputs the message."""
        log_blue("info message")
        output = self.held_output.getvalue()
        self.assertIn("info message", output)

    def test_log_yellow_contains_message(self):
        """Test that log_yellow outputs the message."""
        log_yellow("warning message")
        output = self.held_output.getvalue()
        self.assertIn("warning message", output)

    def test_log_cyan_contains_message(self):
        """Test that log_cyan outputs the message."""
        log_cyan("special message")
        output = self.held_output.getvalue()
        self.assertIn("special message", output)

    def test_log_magenta_contains_message(self):
        """Test that log_magenta outputs the message."""
        log_magenta("highlight message")
        output = self.held_output.getvalue()
        self.assertIn("highlight message", output)

    def test_log_white_contains_message(self):
        """Test that log_white outputs the message."""
        log_white("standard message")
        output = self.held_output.getvalue()
        self.assertIn("standard message", output)

    def test_log_with_multiple_arguments(self):
        """Test log function with multiple arguments."""
        log_red("error", "code:", 404)
        output = self.held_output.getvalue()
        self.assertIn("error code: 404", output)

    def test_log_with_non_string_argument(self):
        """Test log function with non-string argument."""
        log_green(42)
        output = self.held_output.getvalue()
        self.assertIn("42", output)


class TestColoramaAvailability(unittest.TestCase):
    """Test cases for colorama availability checking."""

    def test_is_colorama_available_returns_boolean(self):
        """Test that is_colorama_available returns a boolean."""
        result = is_colorama_available()
        self.assertIsInstance(result, bool)


class TestFallbackBehavior(unittest.TestCase):
    """Test cases for fallback behavior when colorama is not available."""

    def setUp(self):
        """Redirect stdout for testing."""
        self.held_output = StringIO()
        self.original_stdout = sys.stdout
        sys.stdout = self.held_output

    def tearDown(self):
        """Restore stdout."""
        sys.stdout = self.original_stdout

    def test_output_is_printed_regardless_of_colorama(self):
        """Test that output is always printed."""
        log_red("test message")
        output = self.held_output.getvalue()
        self.assertTrue(len(output) > 0)
        self.assertIn("test message", output)


if __name__ == '__main__':
    unittest.main()
