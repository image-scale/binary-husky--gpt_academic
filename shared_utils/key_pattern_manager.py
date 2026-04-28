# API key validation functions
import re


def is_openai_api_key(key):
    """Check if a key matches OpenAI API key patterns."""
    if not isinstance(key, str):
        return False

    # Classic OpenAI API key: sk-{48 alphanumeric chars}
    if re.match(r'^sk-[a-zA-Z0-9]{48}$', key):
        return True

    # Session key: sess-{40 alphanumeric chars}
    if re.match(r'^sess-[a-zA-Z0-9]{40}$', key):
        return True

    # Extended key format: sk-{rest with underscores/hyphens}, must be 95 chars total
    if key.startswith('sk-') and not key.startswith('sk-proj-'):
        if re.match(r'^sk-[a-zA-Z0-9_-]+$', key) and len(key) == 95:
            return True

    # Project-based API key format: sk-proj-{rest}, must be 132 chars total
    if key.startswith('sk-proj-'):
        # Must only contain alphanumeric, underscore, hyphen
        if re.match(r'^sk-proj-[a-zA-Z0-9_-]+$', key):
            if len(key) == 132:
                return True

    return False


def is_azure_api_key(key):
    """Check if a key matches Azure API key pattern (32 hex chars)."""
    if not isinstance(key, str):
        return False
    return bool(re.match(r'^[a-zA-Z0-9]{32}$', key))


def is_api2d_key(key):
    """Check if a key matches API2D key pattern: fk{6 chars}-{32 chars}."""
    if not isinstance(key, str):
        return False
    return bool(re.match(r'^fk[a-zA-Z0-9]{6}-[a-zA-Z0-9]{32}$', key))


def is_any_api_key(key):
    """Check if a key matches any known API key pattern."""
    return is_openai_api_key(key) or is_azure_api_key(key) or is_api2d_key(key)


def what_keys(key):
    """Return a description of what type of key this is."""
    results = []
    if is_openai_api_key(key):
        results.append("OpenAI Key")
    if is_azure_api_key(key):
        results.append("Azure Key")
    if is_api2d_key(key):
        results.append("API2D Key")

    count = len(results)
    if count == 0:
        return "Unknown key type (0 matches)"
    return f"{', '.join(results)} ({count} match{'es' if count > 1 else ''})"


def is_o_family_for_openai(model):
    """Check if the model is in OpenAI's O-family (o1, o1-mini, etc.)."""
    if not isinstance(model, str):
        return False
    # O-family models start with 'o' followed by a digit
    return bool(re.match(r'^o\d', model))
