"""Tests for the API key pattern manager module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.key_pattern_manager import (
    is_openai_api_key,
    is_azure_api_key,
    is_api2d_key,
    is_cohere_api_key,
    is_openrouter_api_key,
    is_any_api_key,
    what_keys,
    select_api_key,
    _is_o_family_model,
)


class TestOpenAIKeyValidation(unittest.TestCase):
    """Test OpenAI API key pattern validation."""

    def test_valid_standard_key_48_chars(self):
        """Test valid OpenAI key with 48 character suffix."""
        key = "sk-" + "a" * 48
        self.assertTrue(is_openai_api_key(key))

    def test_valid_standard_key_92_chars(self):
        """Test valid OpenAI key with 92 character suffix."""
        key = "sk-" + "b" * 92
        self.assertTrue(is_openai_api_key(key))

    def test_valid_project_key_48_chars(self):
        """Test valid project key with 48 character suffix."""
        key = "sk-proj-" + "c" * 48
        self.assertTrue(is_openai_api_key(key))

    def test_valid_project_key_124_chars(self):
        """Test valid project key with 124 character suffix."""
        key = "sk-proj-" + "d" * 124
        self.assertTrue(is_openai_api_key(key))

    def test_valid_project_key_156_chars(self):
        """Test valid project key with 156 character suffix."""
        key = "sk-proj-" + "e" * 156
        self.assertTrue(is_openai_api_key(key))

    def test_valid_session_key(self):
        """Test valid session key with 40 character suffix."""
        key = "sess-" + "f" * 40
        self.assertTrue(is_openai_api_key(key))

    def test_invalid_key_wrong_prefix(self):
        """Test that wrong prefix returns False."""
        key = "sx-" + "a" * 48
        self.assertFalse(is_openai_api_key(key))

    def test_invalid_key_too_short(self):
        """Test that key with wrong length returns False."""
        key = "sk-" + "a" * 30
        self.assertFalse(is_openai_api_key(key))

    def test_invalid_session_key_too_short(self):
        """Test invalid session key with wrong length."""
        key = "sess-" + "f" * 38
        self.assertFalse(is_openai_api_key(key))

    def test_invalid_key_string(self):
        """Test completely invalid key."""
        self.assertFalse(is_openai_api_key("invalid_key"))

    def test_key_with_special_chars(self):
        """Test key with allowed special characters (underscore, hyphen)."""
        # Build a key with underscores and hyphens that totals 48 chars after sk-
        key = "sk-" + "a_b-c_d-e_f-g_h-i_j-k_l-m_n-o_p-q_r-s_t-u_v-w_xy"
        # Verify the length: sk- is 3 chars, then we need 48 more
        suffix_length = len(key) - 3
        self.assertEqual(suffix_length, 48)
        self.assertTrue(is_openai_api_key(key))


class TestAzureKeyValidation(unittest.TestCase):
    """Test Azure API key pattern validation."""

    def test_valid_azure_key(self):
        """Test valid Azure key with 32 alphanumeric chars."""
        key = "a" * 32
        self.assertTrue(is_azure_api_key(key))

    def test_valid_azure_key_mixed(self):
        """Test valid Azure key with mixed case and numbers."""
        key = "aB1cD2eF3gH4iJ5kL6mN7oP8qR9sT0uV"
        self.assertTrue(is_azure_api_key(key))

    def test_invalid_azure_key_too_short(self):
        """Test invalid Azure key with wrong length."""
        key = "a" * 31
        self.assertFalse(is_azure_api_key(key))

    def test_invalid_azure_key_too_long(self):
        """Test invalid Azure key that is too long."""
        key = "a" * 33
        self.assertFalse(is_azure_api_key(key))


class TestAPI2DKeyValidation(unittest.TestCase):
    """Test API2D key pattern validation."""

    def test_valid_api2d_key(self):
        """Test valid API2D key format."""
        key = "fk" + "a" * 6 + "-" + "b" * 32
        self.assertTrue(is_api2d_key(key))

    def test_invalid_api2d_key_wrong_prefix(self):
        """Test invalid API2D key with wrong prefix."""
        key = "fx" + "a" * 6 + "-" + "b" * 32
        self.assertFalse(is_api2d_key(key))

    def test_invalid_api2d_key_no_hyphen(self):
        """Test invalid API2D key without hyphen."""
        key = "fk" + "a" * 6 + "b" * 32
        self.assertFalse(is_api2d_key(key))


class TestCohereKeyValidation(unittest.TestCase):
    """Test Cohere API key pattern validation."""

    def test_valid_cohere_key(self):
        """Test valid Cohere key with 40 chars."""
        key = "a" * 40
        self.assertTrue(is_cohere_api_key(key))

    def test_invalid_cohere_key_too_short(self):
        """Test invalid Cohere key with wrong length."""
        key = "a" * 39
        self.assertFalse(is_cohere_api_key(key))


class TestOpenRouterKeyValidation(unittest.TestCase):
    """Test OpenRouter API key pattern validation."""

    def test_valid_openrouter_key(self):
        """Test valid OpenRouter key format."""
        key = "sk-or-v1-" + "a" * 64
        self.assertTrue(is_openrouter_api_key(key))

    def test_invalid_openrouter_key_wrong_prefix(self):
        """Test invalid OpenRouter key with wrong prefix."""
        key = "sk-or-v2-" + "a" * 64
        self.assertFalse(is_openrouter_api_key(key))


class TestIsAnyApiKey(unittest.TestCase):
    """Test the is_any_api_key function."""

    def test_recognizes_openai_key(self):
        """Test that OpenAI keys are recognized."""
        key = "sk-" + "a" * 48
        self.assertTrue(is_any_api_key(key))

    def test_recognizes_azure_key(self):
        """Test that Azure keys are recognized."""
        key = "a" * 32
        self.assertTrue(is_any_api_key(key))

    def test_recognizes_api2d_key(self):
        """Test that API2D keys are recognized."""
        key = "fk" + "a" * 6 + "-" + "b" * 32
        self.assertTrue(is_any_api_key(key))

    def test_recognizes_multiple_keys(self):
        """Test that comma-separated keys are handled."""
        openai_key = "sk-" + "a" * 48
        azure_key = "b" * 32
        keys = f"{openai_key},{azure_key}"
        self.assertTrue(is_any_api_key(keys))

    def test_rejects_invalid_key(self):
        """Test that invalid keys are rejected."""
        self.assertFalse(is_any_api_key("invalid"))

    def test_rejects_invalid_characters(self):
        """Test that keys with invalid characters are rejected."""
        self.assertFalse(is_any_api_key("key with spaces"))
        self.assertFalse(is_any_api_key("key!@#$%"))


class TestWhatKeys(unittest.TestCase):
    """Test the what_keys function."""

    def test_counts_openai_keys(self):
        """Test counting OpenAI keys."""
        key = "sk-" + "a" * 48
        result = what_keys(key)
        self.assertIn("OpenAI Key 1", result)

    def test_counts_multiple_types(self):
        """Test counting multiple key types."""
        openai_key = "sk-" + "a" * 48
        azure_key = "b" * 32
        api2d_key = "fk" + "c" * 6 + "-" + "d" * 32
        keys = f"{openai_key},{azure_key},{api2d_key}"
        result = what_keys(keys)
        self.assertIn("OpenAI Key 1", result)
        self.assertIn("Azure Key 1", result)
        self.assertIn("API2D Key 1", result)

    def test_counts_multiple_openai_keys(self):
        """Test counting multiple OpenAI keys."""
        key1 = "sk-" + "a" * 48
        key2 = "sk-" + "b" * 48
        keys = f"{key1},{key2}"
        result = what_keys(keys)
        self.assertIn("OpenAI Key 2", result)


class TestSelectApiKey(unittest.TestCase):
    """Test the select_api_key function."""

    def test_selects_openai_key_for_gpt_model(self):
        """Test selecting OpenAI key for GPT model."""
        openai_key = "sk-" + "a" * 48
        azure_key = "b" * 32
        keys = f"{openai_key},{azure_key}"
        result = select_api_key(keys, "gpt-3.5-turbo")
        self.assertEqual(result, openai_key)

    def test_selects_openai_key_for_chatgpt_model(self):
        """Test selecting OpenAI key for ChatGPT model."""
        openai_key = "sk-" + "a" * 48
        keys = openai_key
        result = select_api_key(keys, "chatgpt-4")
        self.assertEqual(result, openai_key)

    def test_selects_azure_key_for_azure_model(self):
        """Test selecting Azure key for Azure model."""
        openai_key = "sk-" + "a" * 48
        azure_key = "b" * 32
        keys = f"{openai_key},{azure_key}"
        result = select_api_key(keys, "azure-gpt-4")
        self.assertEqual(result, azure_key)

    def test_selects_api2d_key_for_api2d_model(self):
        """Test selecting API2D key for API2D model."""
        api2d_key = "fk" + "c" * 6 + "-" + "d" * 32
        keys = api2d_key
        result = select_api_key(keys, "api2d-gpt-4")
        self.assertEqual(result, api2d_key)

    def test_selects_cohere_key_for_cohere_model(self):
        """Test selecting Cohere key for Cohere model."""
        cohere_key = "c" * 40
        keys = cohere_key
        result = select_api_key(keys, "cohere-command")
        self.assertEqual(result, cohere_key)

    def test_raises_error_when_no_matching_key(self):
        """Test that RuntimeError is raised when no key matches."""
        azure_key = "b" * 32
        with self.assertRaises(RuntimeError):
            select_api_key(azure_key, "gpt-3.5-turbo")

    def test_selects_openai_for_o_family_model(self):
        """Test selecting OpenAI key for o-family models."""
        openai_key = "sk-" + "a" * 48
        result = select_api_key(openai_key, "o1-mini")
        self.assertEqual(result, openai_key)


class TestOFamilyModel(unittest.TestCase):
    """Test the _is_o_family_model function."""

    def test_o1_is_o_family(self):
        """Test that o1 is recognized as o-family."""
        self.assertTrue(_is_o_family_model("o1"))

    def test_o1_mini_is_o_family(self):
        """Test that o1-mini is recognized as o-family."""
        self.assertTrue(_is_o_family_model("o1-mini"))

    def test_o2_is_o_family(self):
        """Test that o2 is recognized as o-family."""
        self.assertTrue(_is_o_family_model("o2"))

    def test_gpt_is_not_o_family(self):
        """Test that GPT models are not o-family."""
        self.assertFalse(_is_o_family_model("gpt-4"))

    def test_other_model_not_o_family(self):
        """Test that other models starting with 'o' but not o-family."""
        self.assertFalse(_is_o_family_model("ollama-llama"))


if __name__ == '__main__':
    unittest.main()
