"""Smoke tests for importable modules and pure-logic functions in gpt_academic."""
import os
import sys
import pytest

# Ensure project root is on path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
os.chdir(project_root)


class TestKeyPatternManager:
    """Tests for shared_utils.key_pattern_manager (API key validation)."""

    def test_is_openai_api_key_valid(self):
        from shared_utils.key_pattern_manager import is_openai_api_key
        assert is_openai_api_key("sk-" + "x" * 48) is True

    def test_is_openai_api_key_invalid_prefix(self):
        from shared_utils.key_pattern_manager import is_openai_api_key
        assert is_openai_api_key("sx-" + "x" * 48) is False

    def test_is_openai_api_key_sess_valid(self):
        from shared_utils.key_pattern_manager import is_openai_api_key
        assert is_openai_api_key("sess-" + "x" * 40) is True

    def test_is_openai_api_key_sess_invalid_length(self):
        from shared_utils.key_pattern_manager import is_openai_api_key
        assert is_openai_api_key("sess-" + "x" * 38) is False

    def test_is_openai_api_key_garbage(self):
        from shared_utils.key_pattern_manager import is_openai_api_key
        assert is_openai_api_key("invalid_key") is False

    def test_is_azure_api_key(self):
        from shared_utils.key_pattern_manager import is_azure_api_key
        assert is_azure_api_key("a" * 32) is True
        assert is_azure_api_key("short") is False

    def test_is_api2d_key(self):
        from shared_utils.key_pattern_manager import is_api2d_key
        assert is_api2d_key("fk" + "a" * 6 + "-" + "b" * 32) is True
        assert is_api2d_key("invalid") is False

    def test_is_any_api_key(self):
        from shared_utils.key_pattern_manager import is_any_api_key
        assert is_any_api_key("sk-" + "x" * 48) is True
        assert is_any_api_key("not-a-key!!!") is False

    def test_what_keys(self):
        from shared_utils.key_pattern_manager import what_keys
        result = what_keys("sk-" + "x" * 48)
        assert "OpenAI Key" in result
        assert "1" in result

    def test_is_o_family_for_openai(self):
        from shared_utils.key_pattern_manager import is_o_family_for_openai
        assert is_o_family_for_openai("o1") is True
        assert is_o_family_for_openai("o1-mini") is True
        assert is_o_family_for_openai("gpt-4") is False
        assert is_o_family_for_openai("other") is False


class TestTextMask:
    """Tests for shared_utils.text_mask (string masking for LLM vs render)."""

    def test_apply_mask_no_tag(self):
        from shared_utils.text_mask import apply_gpt_academic_string_mask
        assert apply_gpt_academic_string_mask("hello world", "show_llm") == "hello world"

    def test_build_and_apply_mask_show_llm(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask,
            build_gpt_academic_masked_string,
        )
        masked = build_gpt_academic_masked_string(text_show_llm="LLM_TEXT", text_show_render="RENDER_TEXT")
        result = apply_gpt_academic_string_mask(masked, "show_llm")
        assert "LLM_TEXT" in result
        assert "RENDER_TEXT" not in result

    def test_build_and_apply_mask_show_render(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask,
            build_gpt_academic_masked_string,
        )
        masked = build_gpt_academic_masked_string(text_show_llm="LLM_TEXT", text_show_render="RENDER_TEXT")
        result = apply_gpt_academic_string_mask(masked, "show_render")
        assert "RENDER_TEXT" in result
        assert "LLM_TEXT" not in result

    def test_apply_mask_show_all(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask,
            build_gpt_academic_masked_string,
        )
        masked = build_gpt_academic_masked_string(text_show_llm="A", text_show_render="B")
        result = apply_gpt_academic_string_mask(masked, "show_all")
        assert "A" in result
        assert "B" in result

    def test_apply_mask_invalid_mode(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask,
            build_gpt_academic_masked_string,
        )
        masked = build_gpt_academic_masked_string(text_show_llm="X", text_show_render="Y")
        with pytest.raises(ValueError, match="Invalid mode"):
            apply_gpt_academic_string_mask(masked, "bad_mode")

    def test_langbased_mask_english(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask_langbased,
            build_gpt_academic_masked_string_langbased,
        )
        masked = build_gpt_academic_masked_string_langbased(
            text_show_english="English text", text_show_chinese="Chinese text"
        )
        result = apply_gpt_academic_string_mask_langbased(masked, "hello world")
        assert "English text" in result
        assert "Chinese text" not in result

    def test_langbased_mask_chinese(self):
        from shared_utils.text_mask import (
            apply_gpt_academic_string_mask_langbased,
            build_gpt_academic_masked_string_langbased,
        )
        masked = build_gpt_academic_masked_string_langbased(
            text_show_english="English text", text_show_chinese="Chinese text"
        )
        result = apply_gpt_academic_string_mask_langbased(masked, "你好世界")
        assert "Chinese text" in result
        assert "English text" not in result

    def test_apply_mask_empty_string(self):
        from shared_utils.text_mask import apply_gpt_academic_string_mask
        assert apply_gpt_academic_string_mask("", "show_llm") == ""

    def test_apply_mask_none(self):
        from shared_utils.text_mask import apply_gpt_academic_string_mask
        assert apply_gpt_academic_string_mask(None, "show_llm") is None


class TestColorful:
    """Tests for shared_utils.colorful (colored output functions)."""

    def test_import_colorful(self):
        from shared_utils.colorful import print红, print绿, sprint红, sprint绿
        assert callable(print红)
        assert callable(sprint红)

    def test_sprint_functions(self):
        from shared_utils.colorful import sprint红, sprint绿, sprint蓝
        result = sprint红("hello")
        assert "hello" in result
        assert "\033[" in result
        result_g = sprint绿("world")
        assert "world" in result_g
        result_b = sprint蓝("test")
        assert "test" in result_b


class TestConfigLoader:
    """Tests for shared_utils.config_loader."""

    def test_get_conf_basic(self):
        from shared_utils.config_loader import get_conf
        # Should be able to read basic config values
        result = get_conf("LLM_MODEL")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_get_conf_multiple(self):
        from shared_utils.config_loader import get_conf
        results = get_conf("LLM_MODEL", "USE_PROXY")
        assert isinstance(results, list)
        assert len(results) == 2

    def test_read_env_variable_with_env(self):
        from shared_utils.config_loader import get_conf
        os.environ["GPT_ACADEMIC_USE_PROXY"] = "False"
        from shared_utils.config_loader import read_single_conf_with_lru_cache
        read_single_conf_with_lru_cache.cache_clear()
        get_conf.cache_clear()
        result = get_conf("USE_PROXY")
        assert result is False


class TestAdvancedMarkdown:
    """Tests for shared_utils.advanced_markdown_format."""

    def test_import_advanced_markdown(self):
        from shared_utils.advanced_markdown_format import format_io
        assert callable(format_io)

    def test_format_io_basic(self):
        from shared_utils.advanced_markdown_format import format_io
        # format_io is an unbound method expecting (self, y)
        chatbot = [["Hello", "World"]]
        result = format_io(None, chatbot)
        assert isinstance(result, list)
        assert len(result) == 1


class TestImportModules:
    """Tests that key modules can be imported without errors."""

    def test_import_config(self):
        import config
        assert hasattr(config, "API_KEY")
        assert hasattr(config, "LLM_MODEL")

    def test_import_core_functional(self):
        import core_functional
        # core_functional should define function groups
        assert hasattr(core_functional, "get_core_functions")

    def test_import_version(self):
        import json
        with open("version", "r") as f:
            version_info = json.load(f)
        assert "version" in version_info
