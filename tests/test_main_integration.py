"""Tests for the main integration module."""
import os
import sys
import unittest
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.main_integration import (
    AcademicConfig,
    AcademicToolbox,
    create_toolbox,
    get_system_info,
    initialize_logging,
    polish_text,
    check_grammar,
    translate_text,
    explain_code,
)


class TestAcademicConfig(unittest.TestCase):
    """Test cases for AcademicConfig."""

    def test_create_config_defaults(self):
        """Test creating config with defaults."""
        config = AcademicConfig()
        self.assertEqual(config.llm_model, "gpt-3.5-turbo")
        self.assertEqual(config.web_port, 8080)
        self.assertFalse(config.use_proxy)

    def test_create_config_with_values(self):
        """Test creating config with custom values."""
        config = AcademicConfig(
            api_key="test-key",
            llm_model="gpt-4",
            web_port=9000,
        )
        self.assertEqual(config.api_key, "test-key")
        self.assertEqual(config.llm_model, "gpt-4")
        self.assertEqual(config.web_port, 9000)

    def test_from_config(self):
        """Test creating config from config files."""
        config = AcademicConfig.from_config()
        self.assertIsNotNone(config)
        self.assertIsInstance(config.llm_model, str)


class TestAcademicToolbox(unittest.TestCase):
    """Test cases for AcademicToolbox."""

    def test_create_toolbox(self):
        """Test creating a toolbox."""
        config = AcademicConfig(api_key="test-key")
        toolbox = AcademicToolbox(config)
        self.assertIsNotNone(toolbox)
        self.assertEqual(toolbox.config.api_key, "test-key")

    def test_create_toolbox_default_config(self):
        """Test creating toolbox with default config."""
        toolbox = AcademicToolbox()
        self.assertIsNotNone(toolbox.config)

    def test_set_api_key(self):
        """Test setting API key."""
        toolbox = AcademicToolbox(AcademicConfig())
        toolbox.set_api_key("new-key")
        self.assertEqual(toolbox.config.api_key, "new-key")

    def test_set_model(self):
        """Test setting model."""
        toolbox = AcademicToolbox(AcademicConfig())
        toolbox.set_model("gpt-4")
        self.assertEqual(toolbox.config.llm_model, "gpt-4")

    def test_validate_api_key_invalid(self):
        """Test validating invalid API key."""
        toolbox = AcademicToolbox(AcademicConfig(api_key="invalid"))
        self.assertFalse(toolbox.validate_api_key())

    def test_validate_api_key_valid(self):
        """Test validating valid API key."""
        valid_key = "sk-" + "a" * 48
        toolbox = AcademicToolbox(AcademicConfig(api_key=valid_key))
        self.assertTrue(toolbox.validate_api_key())

    def test_list_core_functions(self):
        """Test listing core functions."""
        toolbox = AcademicToolbox()
        functions = toolbox.list_core_functions()
        self.assertIsInstance(functions, list)
        self.assertIn("Academic Polish", functions)

    def test_format_markdown(self):
        """Test markdown formatting."""
        toolbox = AcademicToolbox()
        result = toolbox.format_markdown("# Hello")
        self.assertIn("Hello", result)
        self.assertIn("markdown-body", result)

    def test_count_tokens(self):
        """Test token counting."""
        toolbox = AcademicToolbox()
        count = toolbox.count_tokens("Hello, world!")
        self.assertGreater(count, 0)

    def test_detect_text_language_english(self):
        """Test detecting English text."""
        toolbox = AcademicToolbox()
        lang = toolbox.detect_text_language("Hello world")
        self.assertEqual(lang, "en")

    def test_detect_text_language_chinese(self):
        """Test detecting Chinese text."""
        toolbox = AcademicToolbox()
        lang = toolbox.detect_text_language("你好世界")
        self.assertEqual(lang, "zh")


class TestToolboxPlugins(unittest.TestCase):
    """Test cases for toolbox plugin functionality."""

    def setUp(self):
        """Create toolbox for tests."""
        from academic_toolbox.plugin_system import clear_plugins
        clear_plugins()
        self.toolbox = AcademicToolbox()

    def tearDown(self):
        """Clean up plugins."""
        from academic_toolbox.plugin_system import clear_plugins
        clear_plugins()

    def test_register_and_call_plugin(self):
        """Test registering and calling a plugin."""
        def double(x):
            return x * 2

        self.toolbox.register_plugin("Double", double)
        result = self.toolbox.call_plugin("Double", 5)
        self.assertEqual(result, 10)

    def test_list_plugins_empty(self):
        """Test listing plugins when empty."""
        plugins = self.toolbox.list_plugins()
        self.assertIsInstance(plugins, list)


class TestToolboxHistory(unittest.TestCase):
    """Test cases for toolbox history functionality."""

    def setUp(self):
        """Create temp directory for tests."""
        self.temp_dir = tempfile.mkdtemp()
        self.toolbox = AcademicToolbox()

    def tearDown(self):
        """Clean up temp directory."""
        shutil.rmtree(self.temp_dir)

    def test_write_history(self):
        """Test writing history to file."""
        history = ["Question 1", "Answer 1", "Question 2", "Answer 2"]
        # Note: This uses the default log folder
        result = self.toolbox.write_history(history)
        self.assertTrue(os.path.exists(result))


class TestCreateToolbox(unittest.TestCase):
    """Test cases for create_toolbox function."""

    def test_create_default(self):
        """Test creating default toolbox."""
        toolbox = create_toolbox()
        self.assertIsNotNone(toolbox)

    def test_create_with_api_key(self):
        """Test creating toolbox with API key."""
        toolbox = create_toolbox(api_key="custom-key")
        self.assertEqual(toolbox.config.api_key, "custom-key")

    def test_create_with_model(self):
        """Test creating toolbox with model."""
        toolbox = create_toolbox(model="gpt-4")
        self.assertEqual(toolbox.config.llm_model, "gpt-4")


class TestGetSystemInfo(unittest.TestCase):
    """Test cases for get_system_info function."""

    def test_returns_dict(self):
        """Test that system info returns a dictionary."""
        info = get_system_info()
        self.assertIsInstance(info, dict)

    def test_contains_required_keys(self):
        """Test that system info contains required keys."""
        info = get_system_info()
        self.assertIn("version", info)
        self.assertIn("llm_model", info)
        self.assertIn("available_models", info)
        self.assertIn("core_functions", info)


class TestInitializeLogging(unittest.TestCase):
    """Test cases for initialize_logging function."""

    def test_returns_path(self):
        """Test that initialize_logging returns a path."""
        result = initialize_logging()
        self.assertIsInstance(result, str)
        self.assertTrue(os.path.exists(result))


class TestPolishText(unittest.TestCase):
    """Test cases for polish_text function."""

    def test_returns_tuple(self):
        """Test that polish_text returns a tuple."""
        result = polish_text("Some text to polish")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_contains_input(self):
        """Test that result contains the input."""
        prompt, history = polish_text("Test text")
        self.assertIn("Test text", prompt)


class TestCheckGrammar(unittest.TestCase):
    """Test cases for check_grammar function."""

    def test_returns_tuple(self):
        """Test that check_grammar returns a tuple."""
        result = check_grammar("Check this sentence.")
        self.assertIsInstance(result, tuple)
        self.assertEqual(len(result), 2)

    def test_contains_input(self):
        """Test that result contains the input."""
        prompt, history = check_grammar("Check this")
        self.assertIn("Check this", prompt)


class TestTranslateText(unittest.TestCase):
    """Test cases for translate_text function."""

    def test_zh_to_en(self):
        """Test Chinese to English translation."""
        prompt, history = translate_text("你好", direction="zh_to_en")
        self.assertIn("你好", prompt)

    def test_en_to_zh(self):
        """Test English to Chinese translation."""
        prompt, history = translate_text("Hello", direction="en_to_zh")
        self.assertIn("Hello", prompt)


class TestExplainCode(unittest.TestCase):
    """Test cases for explain_code function."""

    def test_returns_tuple(self):
        """Test that explain_code returns a tuple."""
        result = explain_code("print('hello')")
        self.assertIsInstance(result, tuple)

    def test_contains_code_block(self):
        """Test that result wraps code in block."""
        prompt, history = explain_code("x = 1")
        self.assertIn("x = 1", prompt)
        self.assertIn("```", prompt)


class TestApplyCoreFunction(unittest.TestCase):
    """Test cases for apply_core_function."""

    def test_academic_polish(self):
        """Test applying academic polish."""
        toolbox = AcademicToolbox()
        prompt, history = toolbox.apply_core_function(
            "Academic Polish",
            "This text needs polishing."
        )
        self.assertIn("This text needs polishing", prompt)

    def test_grammar_check(self):
        """Test applying grammar check."""
        toolbox = AcademicToolbox()
        prompt, history = toolbox.apply_core_function(
            "Grammar Check",
            "Check this sentence"
        )
        self.assertIn("Check this sentence", prompt)


if __name__ == '__main__':
    unittest.main()
