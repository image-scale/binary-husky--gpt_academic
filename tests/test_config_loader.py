"""Tests for the configuration loader module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.config_loader import (
    get_conf,
    set_conf,
    set_multi_conf,
    read_single_conf_with_lru_cache,
    clear_conf_cache,
    read_env_variable,
)


class TestConfigLoader(unittest.TestCase):
    """Test cases for configuration loading functionality."""

    def setUp(self):
        """Clean up environment and cache before each test."""
        clear_conf_cache()
        for key in list(os.environ.keys()):
            if key.startswith('GPT_ACADEMIC_') or key in ['API_KEY', 'WEB_PORT', 'USE_PROXY', 'TEST_LIST', 'TEST_DICT']:
                del os.environ[key]

    def tearDown(self):
        """Clean up after each test."""
        clear_conf_cache()
        for key in list(os.environ.keys()):
            if key.startswith('GPT_ACADEMIC_') or key in ['API_KEY', 'WEB_PORT', 'USE_PROXY', 'TEST_LIST', 'TEST_DICT']:
                del os.environ[key]

    def test_get_conf_single_value_from_config(self):
        """Test getting a single config value from default config."""
        api_key = get_conf("API_KEY")
        self.assertEqual(api_key, "your-api-key-here")

    def test_get_conf_integer_value(self):
        """Test getting an integer configuration value."""
        clear_conf_cache()
        port = get_conf("WEB_PORT")
        self.assertEqual(port, 8080)
        self.assertIsInstance(port, int)

    def test_get_conf_multiple_values(self):
        """Test getting multiple config values at once."""
        clear_conf_cache()
        api_key, port = get_conf("API_KEY", "WEB_PORT")
        self.assertEqual(api_key, "your-api-key-here")
        self.assertEqual(port, 8080)

    def test_env_var_with_prefix_overrides_config(self):
        """Test that GPT_ACADEMIC_ prefixed env var overrides config."""
        os.environ["GPT_ACADEMIC_API_KEY"] = "env-api-key-123"
        clear_conf_cache()
        api_key = get_conf("API_KEY")
        self.assertEqual(api_key, "env-api-key-123")

    def test_env_var_without_prefix_overrides_config(self):
        """Test that plain env var also overrides config."""
        os.environ["API_KEY"] = "plain-env-key-456"
        clear_conf_cache()
        api_key = get_conf("API_KEY")
        self.assertEqual(api_key, "plain-env-key-456")

    def test_boolean_env_var_true(self):
        """Test boolean config from env var with True."""
        os.environ["USE_PROXY"] = "True"
        clear_conf_cache()
        use_proxy = get_conf("USE_PROXY")
        self.assertTrue(use_proxy)
        self.assertIsInstance(use_proxy, bool)

    def test_boolean_env_var_false(self):
        """Test boolean config from env var with False."""
        os.environ["USE_PROXY"] = "False"
        clear_conf_cache()
        use_proxy = get_conf("USE_PROXY")
        self.assertFalse(use_proxy)
        self.assertIsInstance(use_proxy, bool)

    def test_list_env_var(self):
        """Test list config from env var."""
        os.environ["AVAIL_LLM_MODELS"] = '["model-a", "model-b", "model-c"]'
        clear_conf_cache()
        models = get_conf("AVAIL_LLM_MODELS")
        self.assertEqual(models, ["model-a", "model-b", "model-c"])
        self.assertIsInstance(models, list)

    def test_dict_env_var(self):
        """Test dict config from env var."""
        os.environ["API_URL_REDIRECT"] = '{"old_url": "new_url"}'
        clear_conf_cache()
        redirect = get_conf("API_URL_REDIRECT")
        self.assertEqual(redirect, {"old_url": "new_url"})
        self.assertIsInstance(redirect, dict)

    def test_set_conf_updates_value(self):
        """Test that set_conf updates config value."""
        clear_conf_cache()
        set_conf("API_KEY", "new-key-value")
        api_key = get_conf("API_KEY")
        self.assertEqual(api_key, "new-key-value")

    def test_set_multi_conf(self):
        """Test setting multiple config values at once."""
        clear_conf_cache()
        set_multi_conf({"API_KEY": "multi-key", "WEB_PORT": "9090"})
        api_key, port = get_conf("API_KEY", "WEB_PORT")
        self.assertEqual(api_key, "multi-key")
        self.assertEqual(port, 9090)

    def test_cache_is_used(self):
        """Test that caching works for repeated reads."""
        clear_conf_cache()
        val1 = get_conf("API_KEY")
        cache_info = read_single_conf_with_lru_cache.cache_info()
        misses_before = cache_info.misses

        val2 = get_conf("API_KEY")
        cache_info = read_single_conf_with_lru_cache.cache_info()
        hits_after = cache_info.hits

        self.assertEqual(val1, val2)
        self.assertGreater(hits_after, 0)

    def test_cache_cleared_on_set_conf(self):
        """Test that cache is cleared when set_conf is called, allowing fresh reads."""
        clear_conf_cache()
        original_value = get_conf("API_KEY")

        set_conf("API_KEY", "changed-value")
        new_value = get_conf("API_KEY")

        self.assertNotEqual(original_value, new_value)
        self.assertEqual(new_value, "changed-value")


class TestReadEnvVariable(unittest.TestCase):
    """Test cases for read_env_variable function."""

    def tearDown(self):
        """Clean environment after tests."""
        for key in ['TEST_INT', 'TEST_FLOAT', 'TEST_STR']:
            if key in os.environ:
                del os.environ[key]

    def test_read_integer_from_env(self):
        """Test reading integer from env var."""
        os.environ["TEST_INT"] = "42"
        result = read_env_variable("TEST_INT", 0)
        self.assertEqual(result, 42)
        self.assertIsInstance(result, int)

    def test_read_float_from_env(self):
        """Test reading float from env var."""
        os.environ["TEST_FLOAT"] = "3.14"
        result = read_env_variable("TEST_FLOAT", 0.0)
        self.assertAlmostEqual(result, 3.14)
        self.assertIsInstance(result, float)

    def test_read_string_from_env(self):
        """Test reading string from env var."""
        os.environ["TEST_STR"] = "  hello world  "
        result = read_env_variable("TEST_STR", "")
        self.assertEqual(result, "hello world")

    def test_missing_env_var_raises_keyerror(self):
        """Test that missing env var raises KeyError."""
        with self.assertRaises(KeyError):
            read_env_variable("NONEXISTENT_VAR", "default")


if __name__ == '__main__':
    unittest.main()
