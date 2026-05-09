"""Tests for the core functional module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.core_functional import (
    get_core_functions,
    handle_core_functionality,
    get_function_names,
    get_function_config,
    clear_line_break,
)
from academic_toolbox.text_mask import MASK_BEGIN, MASK_END


class TestGetCoreFunctions(unittest.TestCase):
    """Test cases for get_core_functions."""

    def test_returns_dictionary(self):
        """Test that get_core_functions returns a dictionary."""
        result = get_core_functions()
        self.assertIsInstance(result, dict)

    def test_has_required_functions(self):
        """Test that required functions exist."""
        functions = get_core_functions()
        required = ["Academic Polish", "Grammar Check", "Chinese to English", "Explain Code", "Mind Map"]
        for func_name in required:
            self.assertIn(func_name, functions)

    def test_each_function_has_prefix_and_suffix(self):
        """Test that each function has Prefix and Suffix keys."""
        functions = get_core_functions()
        for name, config in functions.items():
            self.assertIn("Prefix", config, f"{name} missing Prefix")
            self.assertIn("Suffix", config, f"{name} missing Suffix")

    def test_academic_polish_uses_masked_string(self):
        """Test that Academic Polish uses bilingual masked strings."""
        functions = get_core_functions()
        prefix = functions["Academic Polish"]["Prefix"]
        self.assertIn(MASK_BEGIN, prefix)
        self.assertIn(MASK_END, prefix)

    def test_grammar_check_has_example(self):
        """Test that Grammar Check includes example format."""
        functions = get_core_functions()
        prefix = functions["Grammar Check"]["Prefix"]
        self.assertIn("Example:", prefix)
        self.assertIn("Original sentence", prefix)
        self.assertIn("Corrected sentence", prefix)

    def test_explain_code_has_code_delimiters(self):
        """Test that Explain Code has code block delimiters."""
        functions = get_core_functions()
        config = functions["Explain Code"]
        self.assertIn("```", config["Prefix"])
        self.assertIn("```", config["Suffix"])

    def test_mind_map_has_mermaid_example(self):
        """Test that Mind Map has mermaid flowchart example."""
        functions = get_core_functions()
        suffix = functions["Mind Map"]["Suffix"]
        self.assertIn("mermaid", suffix)
        self.assertIn("flowchart", suffix)

    def test_academic_translation_uses_masked_string(self):
        """Test that Academic Translation uses bilingual masked strings."""
        functions = get_core_functions()
        prefix = functions["Academic Translation"]["Prefix"]
        self.assertIn(MASK_BEGIN, prefix)
        self.assertIn(MASK_END, prefix)


class TestHandleCoreFunctionality(unittest.TestCase):
    """Test cases for handle_core_functionality."""

    def test_applies_prefix_and_suffix(self):
        """Test that prefix and suffix are applied."""
        inputs = "test input"
        result, history = handle_core_functionality("Chinese to English", inputs, [])
        self.assertIn("translate following sentence to English", result)
        self.assertIn("test input", result)

    def test_applies_preprocess(self):
        """Test that PreProcess function is called."""
        inputs = "line one\nline two"
        result, history = handle_core_functionality("Grammar Check", inputs, [])
        # PreProcess clears line breaks - the user input should have no newlines
        self.assertIn("line one line two", result)

    def test_auto_clear_history(self):
        """Test that AutoClearHistory clears history when True."""
        # Create a custom function with AutoClearHistory
        custom_funcs = {
            "Test Func": {
                "Prefix": "prefix ",
                "Suffix": " suffix",
                "AutoClearHistory": True,
            }
        }
        inputs = "test"
        history = [["q1", "a1"], ["q2", "a2"]]
        result, new_history = handle_core_functionality("Test Func", inputs, history, functions=custom_funcs)
        self.assertEqual(new_history, [])

    def test_history_preserved_when_no_auto_clear(self):
        """Test that history is preserved when AutoClearHistory is False or missing."""
        inputs = "test"
        history = [["q1", "a1"]]
        result, new_history = handle_core_functionality("Chinese to English", inputs, history)
        self.assertEqual(new_history, history)

    def test_masked_string_resolved_for_english_input(self):
        """Test that masked strings resolve to English for English input."""
        inputs = "This is English text to polish"
        result, history = handle_core_functionality("Academic Polish", inputs, [])
        # Should not contain mask markers
        self.assertNotIn(MASK_BEGIN, result)
        self.assertNotIn(MASK_END, result)
        # Should contain English prompt
        self.assertIn("academic paper", result)

    def test_masked_string_resolved_for_chinese_input(self):
        """Test that masked strings resolve to Chinese for Chinese input."""
        inputs = "这是一段中文文本需要润色"
        result, history = handle_core_functionality("Academic Polish", inputs, [])
        # Should not contain mask markers
        self.assertNotIn(MASK_BEGIN, result)
        self.assertNotIn(MASK_END, result)
        # Should contain Chinese prompt
        self.assertIn("学术论文", result)

    def test_raises_keyerror_for_unknown_function(self):
        """Test that KeyError is raised for unknown function."""
        with self.assertRaises(KeyError):
            handle_core_functionality("Nonexistent Function", "test", [])


class TestGetFunctionNames(unittest.TestCase):
    """Test cases for get_function_names."""

    def test_returns_list(self):
        """Test that get_function_names returns a list."""
        result = get_function_names()
        self.assertIsInstance(result, list)

    def test_visible_only_excludes_hidden(self):
        """Test that visible_only=True excludes hidden functions."""
        visible = get_function_names(visible_only=True)
        all_funcs = get_function_names(visible_only=False)
        # English to Chinese has Visible: False
        self.assertNotIn("English to Chinese", visible)
        self.assertIn("English to Chinese", all_funcs)

    def test_includes_visible_functions(self):
        """Test that visible functions are included."""
        visible = get_function_names(visible_only=True)
        self.assertIn("Academic Polish", visible)
        self.assertIn("Grammar Check", visible)


class TestGetFunctionConfig(unittest.TestCase):
    """Test cases for get_function_config."""

    def test_returns_config_dict(self):
        """Test that get_function_config returns a dictionary."""
        result = get_function_config("Academic Polish")
        self.assertIsInstance(result, dict)

    def test_raises_keyerror_for_unknown(self):
        """Test that KeyError is raised for unknown function."""
        with self.assertRaises(KeyError):
            get_function_config("Nonexistent")


class TestClearLineBreak(unittest.TestCase):
    """Test cases for clear_line_break utility."""

    def test_removes_newlines(self):
        """Test that newlines are removed."""
        result = clear_line_break("line1\nline2\nline3")
        self.assertEqual(result, "line1 line2 line3")

    def test_removes_carriage_returns(self):
        """Test that carriage returns are removed."""
        result = clear_line_break("line1\r\nline2")
        self.assertEqual(result, "line1  line2")

    def test_handles_none(self):
        """Test that None input returns None."""
        result = clear_line_break(None)
        self.assertIsNone(result)

    def test_handles_no_breaks(self):
        """Test text without line breaks passes through."""
        result = clear_line_break("no breaks here")
        self.assertEqual(result, "no breaks here")


if __name__ == '__main__':
    unittest.main()
