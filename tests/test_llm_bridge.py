"""Tests for the LLM bridge module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.llm_bridge import (
    ModelInfo,
    TokenCounter,
    register_model,
    get_model_info,
    get_available_models,
    get_max_token,
    get_endpoint,
    get_token_count,
    get_message_token_count,
    build_messages,
    build_payload,
    build_headers,
    verify_endpoint,
    parse_stream_response,
    get_reduce_token_percent,
    OPENAI_ENDPOINT,
    CLAUDE_ENDPOINT,
    LLMBridge,
)


class TestModelInfo(unittest.TestCase):
    """Test cases for ModelInfo dataclass."""

    def test_create_model_info(self):
        """Test creating ModelInfo."""
        info = ModelInfo(
            name="test-model",
            max_token=4096,
            endpoint="https://api.example.com/v1/chat",
        )
        self.assertEqual(info.name, "test-model")
        self.assertEqual(info.max_token, 4096)
        self.assertFalse(info.has_multimodal_capacity)

    def test_model_info_with_all_options(self):
        """Test ModelInfo with all options set."""
        info = ModelInfo(
            name="advanced-model",
            max_token=128000,
            endpoint="https://api.example.com/v1/chat",
            tokenizer_type="gpt4",
            has_multimodal_capacity=True,
            can_multi_thread=False,
            disable_system_prompt=True,
            disable_stream=True,
            force_temperature_one=True,
        )
        self.assertTrue(info.has_multimodal_capacity)
        self.assertFalse(info.can_multi_thread)
        self.assertTrue(info.disable_stream)


class TestTokenCounter(unittest.TestCase):
    """Test cases for TokenCounter."""

    def test_count_tokens_basic(self):
        """Test basic token counting."""
        counter = TokenCounter()
        count = counter.count_tokens("Hello, world!")
        self.assertGreater(count, 0)
        self.assertIsInstance(count, int)

    def test_count_tokens_empty(self):
        """Test counting empty text."""
        counter = TokenCounter()
        count = counter.count_tokens("")
        self.assertEqual(count, 0)

    def test_count_tokens_none(self):
        """Test counting None."""
        counter = TokenCounter()
        count = counter.count_tokens(None)
        self.assertEqual(count, 0)

    def test_count_tokens_cjk(self):
        """Test counting CJK characters."""
        counter = TokenCounter()
        # CJK text should count differently
        count_en = counter.count_tokens("hello")
        count_zh = counter.count_tokens("你好世界")
        self.assertGreater(count_zh, 0)

    def test_count_message_tokens(self):
        """Test counting tokens in messages."""
        counter = TokenCounter()
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
        ]
        count = counter.count_message_tokens(messages)
        self.assertGreater(count, 0)


class TestGetTokenCount(unittest.TestCase):
    """Test cases for get_token_count function."""

    def test_get_token_count_gpt35(self):
        """Test token count with gpt35 tokenizer."""
        count = get_token_count("Hello, world!", "gpt35")
        self.assertGreater(count, 0)

    def test_get_token_count_gpt4(self):
        """Test token count with gpt4 tokenizer."""
        count = get_token_count("Hello, world!", "gpt4")
        self.assertGreater(count, 0)


class TestModelRegistry(unittest.TestCase):
    """Test cases for model registry functions."""

    def test_register_and_get_model(self):
        """Test registering and retrieving a model."""
        test_model = ModelInfo(
            name="test-registry-model",
            max_token=8192,
            endpoint="https://test.example.com/v1/chat",
        )
        register_model(test_model)
        retrieved = get_model_info("test-registry-model")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "test-registry-model")
        self.assertEqual(retrieved.max_token, 8192)

    def test_get_nonexistent_model(self):
        """Test getting a nonexistent model."""
        result = get_model_info("nonexistent-model-xyz")
        self.assertIsNone(result)

    def test_get_available_models(self):
        """Test getting list of available models."""
        models = get_available_models()
        self.assertIsInstance(models, list)
        self.assertIn("gpt-3.5-turbo", models)
        self.assertIn("gpt-4", models)

    def test_get_max_token(self):
        """Test getting max token for a model."""
        max_token = get_max_token("gpt-3.5-turbo")
        self.assertEqual(max_token, 16385)

    def test_get_max_token_default(self):
        """Test getting max token for unknown model."""
        max_token = get_max_token("unknown-model")
        self.assertEqual(max_token, 4096)

    def test_get_endpoint(self):
        """Test getting endpoint for a model."""
        endpoint = get_endpoint("gpt-3.5-turbo")
        self.assertEqual(endpoint, OPENAI_ENDPOINT)

    def test_get_endpoint_default(self):
        """Test getting endpoint for unknown model."""
        endpoint = get_endpoint("unknown-model")
        self.assertEqual(endpoint, OPENAI_ENDPOINT)


class TestBuildMessages(unittest.TestCase):
    """Test cases for build_messages function."""

    def test_build_basic_messages(self):
        """Test building basic messages."""
        messages = build_messages("Hello", [], "You are helpful")
        self.assertEqual(len(messages), 2)
        self.assertEqual(messages[0]["role"], "system")
        self.assertEqual(messages[0]["content"], "You are helpful")
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[1]["content"], "Hello")

    def test_build_messages_with_history(self):
        """Test building messages with history."""
        history = ["First question", "First answer", "Second question", "Second answer"]
        messages = build_messages("Third question", history, "System")
        self.assertEqual(len(messages), 6)  # 1 system + 4 history + 1 current
        self.assertEqual(messages[1]["role"], "user")
        self.assertEqual(messages[2]["role"], "assistant")

    def test_build_messages_no_system(self):
        """Test building messages without system prompt."""
        messages = build_messages("Hello", [], "")
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")

    def test_build_messages_disabled_system(self):
        """Test building messages for model with disabled system prompt."""
        # o1 models have system prompt disabled
        messages = build_messages("Hello", [], "System prompt", "o1-preview")
        # Should skip the system message
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["role"], "user")


class TestBuildPayload(unittest.TestCase):
    """Test cases for build_payload function."""

    def test_build_basic_payload(self):
        """Test building basic payload."""
        messages = [{"role": "user", "content": "Hello"}]
        payload = build_payload(messages, "gpt-3.5-turbo")
        self.assertEqual(payload["model"], "gpt-3.5-turbo")
        self.assertEqual(payload["messages"], messages)
        self.assertTrue(payload["stream"])

    def test_build_payload_with_options(self):
        """Test building payload with options."""
        messages = [{"role": "user", "content": "Hello"}]
        payload = build_payload(
            messages, "gpt-4", temperature=0.7, top_p=0.9, max_tokens=1000
        )
        self.assertEqual(payload["temperature"], 0.7)
        self.assertEqual(payload["top_p"], 0.9)
        self.assertEqual(payload["max_tokens"], 1000)

    def test_build_payload_disabled_stream(self):
        """Test payload for model with disabled streaming."""
        messages = [{"role": "user", "content": "Hello"}]
        payload = build_payload(messages, "o1-preview", stream=True)
        # o1-preview should have stream disabled
        self.assertFalse(payload["stream"])


class TestBuildHeaders(unittest.TestCase):
    """Test cases for build_headers function."""

    def test_build_openai_headers(self):
        """Test building OpenAI headers."""
        headers = build_headers("sk-test123")
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["Authorization"], "Bearer sk-test123")

    def test_build_azure_headers(self):
        """Test building Azure headers."""
        headers = build_headers("azure-key-123", is_azure=True)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertEqual(headers["api-key"], "azure-key-123")


class TestVerifyEndpoint(unittest.TestCase):
    """Test cases for verify_endpoint function."""

    def test_verify_valid_endpoint(self):
        """Test verifying valid endpoint."""
        result = verify_endpoint("https://api.openai.com/v1/chat/completions")
        self.assertEqual(result, "https://api.openai.com/v1/chat/completions")

    def test_verify_invalid_endpoint(self):
        """Test verifying invalid endpoint."""
        with self.assertRaises(ValueError):
            verify_endpoint("")

        with self.assertRaises(ValueError):
            verify_endpoint("not-a-url")


class TestParseStreamResponse(unittest.TestCase):
    """Test cases for parse_stream_response function."""

    def test_parse_valid_chunk(self):
        """Test parsing valid stream chunk."""
        chunk = b'data: {"choices":[{"delta":{"content":"Hello"}}]}'
        result = parse_stream_response(chunk)
        self.assertEqual(result, "Hello")

    def test_parse_done_chunk(self):
        """Test parsing DONE chunk."""
        chunk = b'data: [DONE]'
        result = parse_stream_response(chunk)
        self.assertIsNone(result)

    def test_parse_empty_delta(self):
        """Test parsing chunk with empty delta."""
        chunk = b'data: {"choices":[{"delta":{}}]}'
        result = parse_stream_response(chunk)
        self.assertIsNone(result)

    def test_parse_invalid_chunk(self):
        """Test parsing invalid chunk."""
        chunk = b'invalid data'
        result = parse_stream_response(chunk)
        self.assertIsNone(result)


class TestGetReduceTokenPercent(unittest.TestCase):
    """Test cases for get_reduce_token_percent function."""

    def test_extract_ratio(self):
        """Test extracting token reduction ratio."""
        error = "maximum context length is 4097 tokens. However, your messages resulted in 4870 tokens"
        ratio, excess = get_reduce_token_percent(error)
        self.assertGreater(ratio, 0)
        self.assertLess(ratio, 1)

    def test_no_match_returns_default(self):
        """Test that unmatched error returns default."""
        ratio, excess = get_reduce_token_percent("some other error")
        self.assertEqual(ratio, 0.5)
        self.assertEqual(excess, "unknown")


class TestLLMBridge(unittest.TestCase):
    """Test cases for LLMBridge class."""

    def test_create_bridge(self):
        """Test creating LLMBridge."""
        bridge = LLMBridge(
            api_key="test-key",
            model_name="gpt-3.5-turbo",
        )
        self.assertEqual(bridge.api_key, "test-key")
        self.assertEqual(bridge.model_name, "gpt-3.5-turbo")
        self.assertEqual(bridge.endpoint, OPENAI_ENDPOINT)

    def test_create_bridge_custom_endpoint(self):
        """Test creating LLMBridge with custom endpoint."""
        bridge = LLMBridge(
            api_key="test-key",
            model_name="gpt-4",
            endpoint="https://custom.api.com/v1/chat",
        )
        self.assertEqual(bridge.endpoint, "https://custom.api.com/v1/chat")

    def test_bridge_with_options(self):
        """Test creating LLMBridge with all options."""
        bridge = LLMBridge(
            api_key="test-key",
            model_name="gpt-4",
            endpoint="https://api.example.com",
            timeout=60,
            max_retry=5,
            proxies={"http": "http://proxy:8080"},
        )
        self.assertEqual(bridge.timeout, 60)
        self.assertEqual(bridge.max_retry, 5)
        self.assertIsNotNone(bridge.proxies)


class TestDefaultModels(unittest.TestCase):
    """Test cases for default model initialization."""

    def test_gpt35_registered(self):
        """Test that gpt-3.5-turbo is registered."""
        info = get_model_info("gpt-3.5-turbo")
        self.assertIsNotNone(info)
        self.assertEqual(info.max_token, 16385)

    def test_gpt4_registered(self):
        """Test that gpt-4 is registered."""
        info = get_model_info("gpt-4")
        self.assertIsNotNone(info)
        self.assertEqual(info.max_token, 8192)

    def test_o1_has_special_settings(self):
        """Test that o1 models have special settings."""
        info = get_model_info("o1-preview")
        self.assertIsNotNone(info)
        self.assertTrue(info.disable_stream)
        self.assertTrue(info.disable_system_prompt)
        self.assertTrue(info.force_temperature_one)

    def test_gpt4o_has_multimodal(self):
        """Test that gpt-4o has multimodal capacity."""
        info = get_model_info("gpt-4o")
        self.assertIsNotNone(info)
        self.assertTrue(info.has_multimodal_capacity)


if __name__ == '__main__':
    unittest.main()
