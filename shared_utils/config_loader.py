# Configuration loading functions
import os
from functools import lru_cache


def _convert_value(value):
    """Convert string values to appropriate Python types."""
    if isinstance(value, str):
        # Boolean conversion
        if value.lower() == 'true':
            return True
        if value.lower() == 'false':
            return False
        # Try numeric conversion
        try:
            return int(value)
        except ValueError:
            pass
        try:
            return float(value)
        except ValueError:
            pass
    return value


@lru_cache
def read_single_conf_with_lru_cache(key):
    """Read a single configuration value with LRU caching.

    Priority:
    1. Environment variable (GPT_ACADEMIC_{KEY})
    2. config_private.py (if exists)
    3. config.py
    """
    # Check environment variable first
    env_key = f"GPT_ACADEMIC_{key}"
    if env_key in os.environ:
        return _convert_value(os.environ[env_key])

    # Try config_private.py
    try:
        import config_private
        if hasattr(config_private, key):
            return getattr(config_private, key)
    except ImportError:
        pass

    # Fall back to config.py
    import config
    if hasattr(config, key):
        return getattr(config, key)

    # Key not found
    return None


@lru_cache
def get_conf(*keys):
    """Get one or more configuration values.

    Args:
        *keys: Configuration key(s) to retrieve

    Returns:
        Single value if one key, list of values if multiple keys
    """
    values = [read_single_conf_with_lru_cache(key) for key in keys]

    if len(keys) == 1:
        return values[0]
    return values
