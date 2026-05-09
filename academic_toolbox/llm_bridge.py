"""
LLM Bridge module providing model registry, token counting, and API interfaces.
Supports OpenAI-compatible API endpoints with multi-model routing.
"""
import re
import json
import time
from typing import List, Dict, Optional, Callable, Any, Generator
from functools import lru_cache
from dataclasses import dataclass, field

from .config_loader import get_conf


# Default API endpoints
OPENAI_ENDPOINT = "https://api.openai.com/v1/chat/completions"
AZURE_ENDPOINT_TEMPLATE = "{base}/openai/deployments/{engine}/chat/completions?api-version=2023-05-15"
API2D_ENDPOINT = "https://openai.api2d.net/v1/chat/completions"
CLAUDE_ENDPOINT = "https://api.anthropic.com/v1/messages"
COHERE_ENDPOINT = "https://api.cohere.ai/v1/chat"
OLLAMA_ENDPOINT = "http://localhost:11434/api/chat"


@dataclass
class ModelInfo:
    """Information about a language model."""
    name: str
    max_token: int
    endpoint: str
    tokenizer_type: str = "gpt35"
    has_multimodal_capacity: bool = False
    can_multi_thread: bool = True
    disable_system_prompt: bool = False
    disable_stream: bool = False
    force_temperature_one: bool = False
    extra: Dict[str, Any] = field(default_factory=dict)


class TokenCounter:
    """
    Simple token counter that estimates token count.
    Uses character-based approximation when tiktoken is not available.
    """

    def __init__(self, model_type: str = "gpt35"):
        self.model_type = model_type
        self._tiktoken_encoder = None

    def _load_tiktoken(self):
        """Attempt to load tiktoken for accurate token counting."""
        if self._tiktoken_encoder is not None:
            return self._tiktoken_encoder

        try:
            import tiktoken
            if self.model_type == "gpt4":
                self._tiktoken_encoder = tiktoken.encoding_for_model("gpt-4")
            else:
                self._tiktoken_encoder = tiktoken.encoding_for_model("gpt-3.5-turbo")
            return self._tiktoken_encoder
        except (ImportError, Exception):
            return None

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for

        Returns:
            Estimated token count
        """
        if text is None:
            return 0

        encoder = self._load_tiktoken()
        if encoder is not None:
            try:
                return len(encoder.encode(text, disallowed_special=()))
            except:
                pass

        # Fallback: approximate 4 characters per token for English
        # and 1.5 characters per token for CJK
        cjk_chars = len(re.findall(r'[一-鿿぀-ヿ가-힯]', text))
        other_chars = len(text) - cjk_chars
        return int(cjk_chars / 1.5 + other_chars / 4)

    def count_message_tokens(self, messages: List[Dict]) -> int:
        """
        Count tokens in a list of messages.

        Args:
            messages: List of message dictionaries with 'role' and 'content'

        Returns:
            Total token count
        """
        total = 0
        for msg in messages:
            total += 4  # message overhead
            for key, value in msg.items():
                if isinstance(value, str):
                    total += self.count_tokens(value)
        total += 2  # priming tokens
        return total


# Global token counters
_token_counter_gpt35 = TokenCounter("gpt35")
_token_counter_gpt4 = TokenCounter("gpt4")


def get_token_count(text: str, model_type: str = "gpt35") -> int:
    """
    Get token count for text.

    Args:
        text: Text to count tokens for
        model_type: Either "gpt35" or "gpt4"

    Returns:
        Token count
    """
    if model_type == "gpt4":
        return _token_counter_gpt4.count_tokens(text)
    return _token_counter_gpt35.count_tokens(text)


def get_message_token_count(messages: List[Dict], model_type: str = "gpt35") -> int:
    """
    Get token count for messages.

    Args:
        messages: List of message dictionaries
        model_type: Either "gpt35" or "gpt4"

    Returns:
        Token count
    """
    if model_type == "gpt4":
        return _token_counter_gpt4.count_message_tokens(messages)
    return _token_counter_gpt35.count_message_tokens(messages)


# Model registry
_model_registry: Dict[str, ModelInfo] = {}


def register_model(model_info: ModelInfo) -> None:
    """
    Register a model in the registry.

    Args:
        model_info: ModelInfo object describing the model
    """
    _model_registry[model_info.name] = model_info


def get_model_info(model_name: str) -> Optional[ModelInfo]:
    """
    Get information about a model.

    Args:
        model_name: Name of the model

    Returns:
        ModelInfo object or None if not found
    """
    return _model_registry.get(model_name)


def get_available_models() -> List[str]:
    """
    Get list of available model names.

    Returns:
        List of model names
    """
    return list(_model_registry.keys())


def get_max_token(model_name: str) -> int:
    """
    Get maximum token limit for a model.

    Args:
        model_name: Name of the model

    Returns:
        Maximum token count, or 4096 as default
    """
    info = get_model_info(model_name)
    if info is not None:
        return info.max_token
    return 4096


def get_endpoint(model_name: str) -> str:
    """
    Get API endpoint for a model.

    Args:
        model_name: Name of the model

    Returns:
        Endpoint URL
    """
    info = get_model_info(model_name)
    if info is not None:
        return info.endpoint
    return OPENAI_ENDPOINT


def _init_default_models() -> None:
    """Initialize default model configurations."""
    # OpenAI models
    openai_models = [
        ("gpt-3.5-turbo", 16385, "gpt35"),
        ("gpt-3.5-turbo-16k", 16385, "gpt35"),
        ("gpt-4", 8192, "gpt4"),
        ("gpt-4-32k", 32768, "gpt4"),
        ("gpt-4-turbo", 128000, "gpt4"),
        ("gpt-4-turbo-preview", 128000, "gpt4"),
        ("gpt-4o", 128000, "gpt4"),
        ("gpt-4o-mini", 128000, "gpt4"),
        ("o1-preview", 128000, "gpt4"),
        ("o1-mini", 128000, "gpt4"),
        ("o1", 200000, "gpt4"),
    ]

    for name, max_tokens, tokenizer in openai_models:
        multimodal = name in ("gpt-4o", "gpt-4o-mini", "gpt-4-turbo")
        disable_stream = name.startswith("o1")
        disable_sys = name.startswith("o1")
        force_temp = name.startswith("o1")

        register_model(ModelInfo(
            name=name,
            max_token=max_tokens,
            endpoint=OPENAI_ENDPOINT,
            tokenizer_type=tokenizer,
            has_multimodal_capacity=multimodal,
            disable_system_prompt=disable_sys,
            disable_stream=disable_stream,
            force_temperature_one=force_temp,
        ))


# Initialize default models
_init_default_models()


def build_messages(
    user_input: str,
    history: List[str],
    system_prompt: str = "",
    model_name: str = "gpt-3.5-turbo"
) -> List[Dict]:
    """
    Build message list for API request.

    Args:
        user_input: Current user input
        history: Previous conversation history (alternating user/assistant)
        system_prompt: System prompt
        model_name: Name of the model (for special handling)

    Returns:
        List of message dictionaries
    """
    messages = []

    # Add system prompt if not disabled
    model_info = get_model_info(model_name)
    if system_prompt and (model_info is None or not model_info.disable_system_prompt):
        messages.append({"role": "system", "content": system_prompt})

    # Add history
    for i, content in enumerate(history):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": content})

    # Add current input
    messages.append({"role": "user", "content": user_input})

    return messages


def build_payload(
    messages: List[Dict],
    model_name: str,
    temperature: float = 1.0,
    top_p: float = 1.0,
    max_tokens: Optional[int] = None,
    stream: bool = True,
) -> Dict:
    """
    Build request payload for API.

    Args:
        messages: List of message dictionaries
        model_name: Name of the model
        temperature: Sampling temperature
        top_p: Top-p sampling parameter
        max_tokens: Maximum tokens to generate
        stream: Whether to stream the response

    Returns:
        Request payload dictionary
    """
    model_info = get_model_info(model_name)

    # Handle special model requirements
    if model_info and model_info.force_temperature_one:
        temperature = 1.0

    if model_info and model_info.disable_stream:
        stream = False

    payload = {
        "model": model_name,
        "messages": messages,
        "temperature": temperature,
        "top_p": top_p,
        "stream": stream,
    }

    if max_tokens is not None:
        payload["max_tokens"] = max_tokens

    return payload


def build_headers(api_key: str, is_azure: bool = False) -> Dict[str, str]:
    """
    Build request headers.

    Args:
        api_key: API key
        is_azure: Whether this is an Azure endpoint

    Returns:
        Headers dictionary
    """
    if is_azure:
        return {
            "Content-Type": "application/json",
            "api-key": api_key,
        }
    else:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        }


@lru_cache(maxsize=32)
def verify_endpoint(endpoint: str) -> str:
    """
    Verify that an endpoint URL is valid.

    Args:
        endpoint: Endpoint URL to verify

    Returns:
        The endpoint if valid

    Raises:
        ValueError: If endpoint appears invalid
    """
    if not endpoint or not endpoint.startswith("http"):
        raise ValueError(f"Invalid endpoint: {endpoint}")
    return endpoint


def parse_stream_response(chunk: bytes) -> Optional[str]:
    """
    Parse a streamed response chunk.

    Args:
        chunk: Raw response chunk

    Returns:
        Extracted content text, or None if no content
    """
    try:
        decoded = chunk.decode('utf-8')
        if not decoded.startswith('data:'):
            return None

        if 'data: [DONE]' in decoded:
            return None

        json_str = decoded[6:].strip()
        if not json_str:
            return None

        data = json.loads(json_str)

        if 'choices' not in data or len(data['choices']) == 0:
            return None

        delta = data['choices'][0].get('delta', {})
        return delta.get('content')

    except (json.JSONDecodeError, UnicodeDecodeError, KeyError):
        return None


def get_reduce_token_percent(error_text: str) -> tuple:
    """
    Extract token reduction ratio from error message.

    Args:
        error_text: Error message text

    Returns:
        Tuple of (reduction_ratio, excess_tokens_str)
    """
    try:
        pattern = r"(\d+)\s+tokens\b"
        matches = re.findall(pattern, error_text)
        if len(matches) >= 2:
            max_limit = float(matches[0]) - 500  # leave some margin
            current_tokens = float(matches[1])
            ratio = max_limit / current_tokens
            if 0 < ratio < 1:
                return ratio, str(int(current_tokens - max_limit))
    except:
        pass
    return 0.5, "unknown"


class LLMBridge:
    """
    Bridge class for making LLM API calls.
    Supports OpenAI-compatible APIs with streaming.
    """

    def __init__(
        self,
        api_key: str,
        model_name: str = "gpt-3.5-turbo",
        endpoint: Optional[str] = None,
        timeout: int = 120,
        max_retry: int = 3,
        proxies: Optional[Dict] = None,
    ):
        """
        Initialize the LLM bridge.

        Args:
            api_key: API key for authentication
            model_name: Name of the model to use
            endpoint: API endpoint (uses model default if not specified)
            timeout: Request timeout in seconds
            max_retry: Maximum retry attempts
            proxies: Proxy configuration
        """
        self.api_key = api_key
        self.model_name = model_name
        self.endpoint = endpoint or get_endpoint(model_name)
        self.timeout = timeout
        self.max_retry = max_retry
        self.proxies = proxies

    def predict(
        self,
        user_input: str,
        history: List[str] = None,
        system_prompt: str = "",
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
    ) -> str:
        """
        Send a request and get the complete response.

        Args:
            user_input: User's input text
            history: Previous conversation history
            system_prompt: System prompt
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Complete response text
        """
        if history is None:
            history = []

        result = ""
        for chunk in self.predict_stream(
            user_input, history, system_prompt, temperature, top_p, max_tokens
        ):
            result += chunk

        return result

    def predict_stream(
        self,
        user_input: str,
        history: List[str] = None,
        system_prompt: str = "",
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """
        Send a request and yield response chunks.

        Args:
            user_input: User's input text
            history: Previous conversation history
            system_prompt: System prompt
            temperature: Sampling temperature
            top_p: Top-p sampling parameter
            max_tokens: Maximum tokens to generate

        Yields:
            Response text chunks
        """
        try:
            import requests
        except ImportError:
            raise ImportError("requests library is required for LLMBridge")

        if history is None:
            history = []

        messages = build_messages(user_input, history, system_prompt, self.model_name)

        model_info = get_model_info(self.model_name)
        stream = True
        if model_info and model_info.disable_stream:
            stream = False

        payload = build_payload(
            messages, self.model_name, temperature, top_p, max_tokens, stream
        )

        is_azure = "azure" in self.endpoint.lower()
        headers = build_headers(self.api_key, is_azure)

        retry = 0
        while True:
            try:
                response = requests.post(
                    verify_endpoint(self.endpoint),
                    headers=headers,
                    json=payload,
                    stream=stream,
                    timeout=self.timeout,
                    proxies=self.proxies,
                )
                break
            except requests.exceptions.Timeout:
                retry += 1
                if retry > self.max_retry:
                    raise TimeoutError("Request timed out after max retries")

        if not stream:
            # Non-streaming response
            data = response.json()
            content = data['choices'][0]['message']['content']
            yield content
            return

        # Streaming response
        for chunk in response.iter_lines():
            if not chunk:
                continue
            content = parse_stream_response(chunk)
            if content:
                yield content
