"""
Configuration loader module.
Handles loading configuration from environment variables, private config, and default config.
Priority: environment variable > config_private.py > config.py
"""
import importlib
import os
from functools import lru_cache


def read_env_variable(arg, default_value):
    """
    Read configuration from environment variables.
    Supports both GPT_ACADEMIC_<CONFIG> and plain <CONFIG> variable names.

    Args:
        arg: The configuration key name
        default_value: The default value used for type inference

    Returns:
        The environment variable value converted to the appropriate type

    Raises:
        KeyError: If environment variable is not found or conversion fails
    """
    arg_with_prefix = "GPT_ACADEMIC_" + arg

    if arg_with_prefix in os.environ:
        env_arg = os.environ[arg_with_prefix]
    elif arg in os.environ:
        env_arg = os.environ[arg]
    else:
        raise KeyError(f"Environment variable {arg} not found")

    try:
        if isinstance(default_value, bool):
            env_arg = env_arg.strip()
            if env_arg == 'True':
                return True
            elif env_arg == 'False':
                return False
            else:
                return default_value
        elif isinstance(default_value, int):
            return int(env_arg)
        elif isinstance(default_value, float):
            return float(env_arg)
        elif isinstance(default_value, str):
            return env_arg.strip()
        elif isinstance(default_value, dict):
            return eval(env_arg)
        elif isinstance(default_value, list):
            return eval(env_arg)
        elif default_value is None:
            if arg == "proxies":
                return eval(env_arg)
            return env_arg.strip()
        else:
            raise KeyError(f"Unsupported type for {arg}")
    except Exception:
        raise KeyError(f"Failed to load environment variable {arg}")


@lru_cache(maxsize=128)
def read_single_conf_with_lru_cache(arg):
    """
    Read a single configuration value with LRU caching.

    Priority:
    1. Environment variable (GPT_ACADEMIC_<key> or <key>)
    2. config_private.py (if exists)
    3. config.py (default)

    Args:
        arg: The configuration key to read

    Returns:
        The configuration value
    """
    try:
        default_ref = getattr(importlib.import_module('config'), arg)
        return read_env_variable(arg, default_ref)
    except KeyError:
        pass

    try:
        return getattr(importlib.import_module('config_private'), arg)
    except (ModuleNotFoundError, AttributeError):
        pass

    return getattr(importlib.import_module('config'), arg)


def get_conf(*args):
    """
    Get one or more configuration values.

    Args:
        *args: Configuration key(s) to retrieve

    Returns:
        Single value if one arg provided, tuple of values if multiple args

    Examples:
        >>> api_key = get_conf("API_KEY")
        >>> api_key, port = get_conf("API_KEY", "WEB_PORT")
    """
    res = []
    for arg in args:
        r = read_single_conf_with_lru_cache(arg)
        res.append(r)

    if len(res) == 1:
        return res[0]
    return tuple(res)


def set_conf(key, value):
    """
    Set a configuration value by updating the environment variable.
    Clears the LRU cache to ensure fresh reads.

    Args:
        key: Configuration key to set
        value: New value for the configuration

    Returns:
        The new value after setting
    """
    read_single_conf_with_lru_cache.cache_clear()
    get_conf.cache_clear() if hasattr(get_conf, 'cache_clear') else None
    os.environ[key] = str(value)
    return get_conf(key)


def set_multi_conf(conf_dict):
    """
    Set multiple configuration values at once.

    Args:
        conf_dict: Dictionary of key-value pairs to set
    """
    for k, v in conf_dict.items():
        set_conf(k, v)


def clear_conf_cache():
    """Clear all configuration caches."""
    read_single_conf_with_lru_cache.cache_clear()
