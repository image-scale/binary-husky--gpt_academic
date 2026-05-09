"""
API key pattern manager module.
Handles validation and selection of API keys for different providers (OpenAI, Azure, API2D, etc.)
"""
import re
import random
from functools import lru_cache


# OpenAI API key patterns
# Matches various OpenAI key formats:
# - sk-<48 chars>: Standard API key
# - sk-<92 chars>: Extended key format
# - sk-proj-<48 chars>: Project key (short)
# - sk-proj-<124 chars>: Project key (medium)
# - sk-proj-<156 chars>: Project key (long)
# - sess-<40 chars>: Session key
OPENAI_KEY_PATTERN = re.compile(
    r"sk-[a-zA-Z0-9_-]{48}$|"
    r"sk-[a-zA-Z0-9_-]{92}$|"
    r"sk-proj-[a-zA-Z0-9_-]{48}$|"
    r"sk-proj-[a-zA-Z0-9_-]{124}$|"
    r"sk-proj-[a-zA-Z0-9_-]{156}$|"
    r"sess-[a-zA-Z0-9]{40}$"
)

# Azure API key pattern: 32 alphanumeric characters
AZURE_KEY_PATTERN = re.compile(r"[a-zA-Z0-9]{32}$")

# API2D key pattern: fk<6 chars>-<32 chars>
API2D_KEY_PATTERN = re.compile(r"fk[a-zA-Z0-9]{6}-[a-zA-Z0-9]{32}$")

# OpenRouter key pattern: sk-or-v1-<64 chars>
OPENROUTER_KEY_PATTERN = re.compile(r"sk-or-v1-[a-zA-Z0-9]{64}$")

# Cohere key pattern: 40 alphanumeric characters
COHERE_KEY_PATTERN = re.compile(r"[a-zA-Z0-9]{40}$")

# Generic valid key character pattern
VALID_KEY_CHARS_PATTERN = re.compile(r"^[a-zA-Z0-9_\-,]+$")


def _get_custom_pattern():
    """Get custom API key pattern from config if set."""
    try:
        from academic_toolbox.config_loader import get_conf
        return get_conf('CUSTOM_API_KEY_PATTERN')
    except Exception:
        return ""


def is_openai_api_key(key):
    """
    Check if a key matches OpenAI API key patterns.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches an OpenAI pattern, False otherwise
    """
    custom_pattern = _get_custom_pattern()
    if custom_pattern:
        return bool(re.match(custom_pattern, key))
    return bool(OPENAI_KEY_PATTERN.match(key))


def is_azure_api_key(key):
    """
    Check if a key matches Azure API key pattern.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches Azure pattern, False otherwise
    """
    return bool(AZURE_KEY_PATTERN.match(key))


def is_api2d_key(key):
    """
    Check if a key matches API2D key pattern.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches API2D pattern, False otherwise
    """
    return bool(API2D_KEY_PATTERN.match(key))


def is_openrouter_api_key(key):
    """
    Check if a key matches OpenRouter API key pattern.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches OpenRouter pattern, False otherwise
    """
    return bool(OPENROUTER_KEY_PATTERN.match(key))


def is_cohere_api_key(key):
    """
    Check if a key matches Cohere API key pattern.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches Cohere pattern, False otherwise
    """
    return bool(COHERE_KEY_PATTERN.match(key))


def is_any_api_key(key):
    """
    Check if a key matches any known API key pattern.
    Supports comma-separated multiple keys.

    Args:
        key: The API key string to validate

    Returns:
        True if the key matches any known pattern, False otherwise
    """
    if not VALID_KEY_CHARS_PATTERN.match(key):
        custom_pattern = _get_custom_pattern()
        if custom_pattern:
            return bool(re.match(custom_pattern, key))
        return False

    if ',' in key:
        keys = key.split(',')
        for k in keys:
            if is_any_api_key(k.strip()):
                return True
        return False
    else:
        return (is_openai_api_key(key) or
                is_api2d_key(key) or
                is_azure_api_key(key) or
                is_cohere_api_key(key) or
                is_openrouter_api_key(key))


def what_keys(keys):
    """
    Analyze and count API keys by type.

    Args:
        keys: Comma-separated string of API keys

    Returns:
        String summarizing the count of each key type
    """
    counts = {'OpenAI Key': 0, 'Azure Key': 0, 'API2D Key': 0}
    key_list = keys.split(',')

    for k in key_list:
        k = k.strip()
        if is_openai_api_key(k):
            counts['OpenAI Key'] += 1
        elif is_api2d_key(k):
            counts['API2D Key'] += 1
        elif is_azure_api_key(k):
            counts['Azure Key'] += 1

    return (f"Detected: OpenAI Key {counts['OpenAI Key']}, "
            f"Azure Key {counts['Azure Key']}, "
            f"API2D Key {counts['API2D Key']}")


def select_api_key(keys, llm_model):
    """
    Select an appropriate API key for the given model type.
    Performs random load balancing among matching keys.

    Args:
        keys: Comma-separated string of API keys
        llm_model: The model identifier string

    Returns:
        A randomly selected key matching the model requirements

    Raises:
        RuntimeError: If no matching key is found for the model
    """
    available_keys = []
    key_list = keys.split(',')

    # OpenAI models (gpt-*, chatgpt-*, one-api-*, o1-*, etc.)
    if (llm_model.startswith('gpt-') or
        llm_model.startswith('chatgpt-') or
        llm_model.startswith('one-api-') or
        _is_o_family_model(llm_model)):
        for k in key_list:
            k = k.strip()
            if is_openai_api_key(k):
                available_keys.append(k)

    # API2D models
    elif llm_model.startswith('api2d-'):
        for k in key_list:
            k = k.strip()
            if is_api2d_key(k):
                available_keys.append(k)

    # Azure models
    elif llm_model.startswith('azure-'):
        for k in key_list:
            k = k.strip()
            if is_azure_api_key(k):
                available_keys.append(k)

    # Cohere models
    elif llm_model.startswith('cohere-'):
        for k in key_list:
            k = k.strip()
            if is_cohere_api_key(k):
                available_keys.append(k)

    # OpenRouter models
    elif llm_model.startswith('openrouter-'):
        for k in key_list:
            k = k.strip()
            if is_openrouter_api_key(k):
                available_keys.append(k)

    if len(available_keys) == 0:
        raise RuntimeError(
            f"No API key found for model {llm_model}. "
            f"Please provide a key that matches the model requirements."
        )

    return random.choice(available_keys)


def _is_o_family_model(llm_model):
    """
    Check if model belongs to the OpenAI o-family (o1, o2, etc.).

    Args:
        llm_model: The model identifier string

    Returns:
        True if model is an o-family model
    """
    if not llm_model.startswith('o'):
        return False
    if llm_model in ['o1', 'o2', 'o3', 'o4', 'o5', 'o6', 'o7', 'o8']:
        return True
    if len(llm_model) >= 3 and llm_model[:3] in ['o1-', 'o2-', 'o3-', 'o4-', 'o5-', 'o6-', 'o7-', 'o8-']:
        return True
    return False
