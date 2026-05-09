"""
Plugin system module providing registration and dispatch of function plugins.
Supports hot reload functionality for development and dynamic plugin loading.
"""
import importlib
import inspect
from functools import wraps
from typing import Dict, List, Callable, Optional, Any, Generator
from dataclasses import dataclass, field

from .config_loader import get_conf


@dataclass
class PluginInfo:
    """Information about a registered plugin."""
    name: str
    function: Callable
    group: str = "default"
    color: str = "secondary"
    as_button: bool = True
    info: str = ""
    advanced_args: bool = False
    args_reminder: str = ""
    visible: bool = True
    extra: Dict[str, Any] = field(default_factory=dict)


# Global plugin registry
_plugin_registry: Dict[str, PluginInfo] = {}


def hot_reload(func: Callable) -> Callable:
    """
    Decorator for hot-reloading plugin functions.
    When PLUGIN_HOT_RELOAD is enabled, the function is reloaded from its
    module before each execution, allowing code changes to take effect
    without restarting the application.

    Args:
        func: The function to wrap

    Returns:
        Wrapped function with hot reload capability
    """
    if get_conf("PLUGIN_HOT_RELOAD"):
        @wraps(func)
        def decorated(*args, **kwargs):
            fn_name = func.__name__
            module = inspect.getmodule(func)
            if module is not None:
                reloaded_module = importlib.reload(module)
                reloaded_func = getattr(reloaded_module, fn_name)
                result = reloaded_func(*args, **kwargs)
                if inspect.isgenerator(result):
                    yield from result
                else:
                    return result
            else:
                result = func(*args, **kwargs)
                if inspect.isgenerator(result):
                    yield from result
                else:
                    return result

        return decorated
    else:
        return func


def register_plugin(
    name: str,
    function: Callable,
    group: str = "default",
    color: str = "secondary",
    as_button: bool = True,
    info: str = "",
    advanced_args: bool = False,
    args_reminder: str = "",
    visible: bool = True,
    **kwargs
) -> PluginInfo:
    """
    Register a plugin function.

    Args:
        name: Display name of the plugin
        function: The plugin function to register
        group: Group category (e.g., "编程", "学术", "对话")
        color: Button color ("primary", "secondary", "stop")
        as_button: Whether to show as a button (vs dropdown)
        info: Description of what the plugin does
        advanced_args: Whether plugin accepts advanced arguments
        args_reminder: Help text for advanced arguments
        visible: Whether the plugin is visible in UI
        **kwargs: Additional metadata

    Returns:
        The created PluginInfo object
    """
    plugin_info = PluginInfo(
        name=name,
        function=function,
        group=group,
        color=color,
        as_button=as_button,
        info=info,
        advanced_args=advanced_args,
        args_reminder=args_reminder,
        visible=visible,
        extra=kwargs,
    )
    _plugin_registry[name] = plugin_info
    return plugin_info


def unregister_plugin(name: str) -> bool:
    """
    Unregister a plugin by name.

    Args:
        name: Name of the plugin to unregister

    Returns:
        True if plugin was found and removed, False otherwise
    """
    if name in _plugin_registry:
        del _plugin_registry[name]
        return True
    return False


def get_plugin(name: str) -> Optional[PluginInfo]:
    """
    Get a plugin by name.

    Args:
        name: Name of the plugin

    Returns:
        PluginInfo object or None if not found
    """
    return _plugin_registry.get(name)


def get_all_plugins() -> Dict[str, PluginInfo]:
    """
    Get all registered plugins.

    Returns:
        Dictionary mapping plugin names to PluginInfo objects
    """
    return _plugin_registry.copy()


def get_plugins_by_group(group: str) -> List[PluginInfo]:
    """
    Get plugins belonging to a specific group.

    Args:
        group: Group name to filter by

    Returns:
        List of plugins in the specified group
    """
    result = []
    for plugin in _plugin_registry.values():
        groups = plugin.group.split("|")
        if group in groups:
            result.append(plugin)
    return result


def get_all_groups() -> List[str]:
    """
    Get list of all plugin groups.

    Returns:
        Sorted list of unique group names
    """
    groups = set()
    for plugin in _plugin_registry.values():
        for group in plugin.group.split("|"):
            groups.add(group.strip())
    return sorted(list(groups))


def get_button_plugins() -> List[PluginInfo]:
    """
    Get plugins that should be displayed as buttons.

    Returns:
        List of plugins with as_button=True
    """
    return [p for p in _plugin_registry.values() if p.as_button and p.visible]


def get_dropdown_plugins() -> List[PluginInfo]:
    """
    Get plugins that should be in the dropdown menu.

    Returns:
        List of plugins with as_button=False
    """
    return [p for p in _plugin_registry.values() if not p.as_button and p.visible]


def dispatch_plugin(
    name: str,
    *args,
    **kwargs
) -> Any:
    """
    Dispatch a call to a registered plugin.

    Args:
        name: Name of the plugin to call
        *args: Positional arguments to pass to the plugin
        **kwargs: Keyword arguments to pass to the plugin

    Returns:
        Result from the plugin function

    Raises:
        KeyError: If plugin is not found
    """
    plugin = get_plugin(name)
    if plugin is None:
        raise KeyError(f"Plugin '{name}' not found")

    return plugin.function(*args, **kwargs)


def clear_plugins() -> None:
    """Clear all registered plugins."""
    _plugin_registry.clear()


def plugin(
    name: str = None,
    group: str = "default",
    color: str = "secondary",
    as_button: bool = True,
    info: str = "",
    advanced_args: bool = False,
    args_reminder: str = "",
    visible: bool = True,
    **kwargs
) -> Callable:
    """
    Decorator to register a function as a plugin.

    Usage:
        @plugin(name="My Plugin", group="tools", info="Does something useful")
        def my_plugin_function(inputs, llm_kwargs, ...):
            ...

    Args:
        name: Plugin name (defaults to function name)
        group: Group category
        color: Button color
        as_button: Show as button
        info: Description
        advanced_args: Accepts advanced args
        args_reminder: Help text
        visible: Show in UI
        **kwargs: Extra metadata

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        plugin_name = name if name is not None else func.__name__
        register_plugin(
            name=plugin_name,
            function=func,
            group=group,
            color=color,
            as_button=as_button,
            info=info,
            advanced_args=advanced_args,
            args_reminder=args_reminder,
            visible=visible,
            **kwargs,
        )
        return func

    return decorator


def load_plugins_from_dict(plugins_dict: Dict[str, Dict]) -> List[PluginInfo]:
    """
    Load plugins from a dictionary (compatible with crazy_functional format).

    Args:
        plugins_dict: Dictionary mapping plugin names to configurations

    Returns:
        List of created PluginInfo objects
    """
    loaded = []
    for name, config in plugins_dict.items():
        func = config.get("Function")
        if func is None:
            continue

        plugin_info = register_plugin(
            name=name,
            function=func,
            group=config.get("Group", "default"),
            color=config.get("Color", "secondary"),
            as_button=config.get("AsButton", True),
            info=config.get("Info", ""),
            advanced_args=config.get("AdvancedArgs", False),
            args_reminder=config.get("ArgsReminder", ""),
            visible=config.get("Visible", True),
        )
        loaded.append(plugin_info)

    return loaded


def to_legacy_format() -> Dict[str, Dict]:
    """
    Export plugins to legacy dictionary format (crazy_functional compatible).

    Returns:
        Dictionary in legacy format
    """
    result = {}
    for name, plugin in _plugin_registry.items():
        result[name] = {
            "Group": plugin.group,
            "Color": plugin.color,
            "AsButton": plugin.as_button,
            "Info": plugin.info,
            "Function": plugin.function,
            "AdvancedArgs": plugin.advanced_args,
            "ArgsReminder": plugin.args_reminder,
            "Visible": plugin.visible,
        }
    return result


def match_group(plugin_groups: str, selected_groups: List[str]) -> bool:
    """
    Check if a plugin's groups match any of the selected groups.

    Args:
        plugin_groups: Pipe-separated group string (e.g., "编程|学术")
        selected_groups: List of selected group names

    Returns:
        True if any group matches
    """
    groups = [g.strip() for g in plugin_groups.split("|")]
    return any(g in selected_groups for g in groups)


class PluginManager:
    """
    Manager class for handling plugin lifecycle.
    Provides methods for loading, reloading, and managing plugins.
    """

    def __init__(self):
        self._loaded_modules: Dict[str, Any] = {}

    def load_plugin_module(self, module_name: str) -> Optional[Any]:
        """
        Load a plugin module by name.

        Args:
            module_name: Fully qualified module name

        Returns:
            Loaded module or None if failed
        """
        try:
            module = importlib.import_module(module_name)
            self._loaded_modules[module_name] = module
            return module
        except ImportError:
            return None

    def reload_plugin_module(self, module_name: str) -> Optional[Any]:
        """
        Reload a previously loaded plugin module.

        Args:
            module_name: Fully qualified module name

        Returns:
            Reloaded module or None if failed
        """
        if module_name not in self._loaded_modules:
            return self.load_plugin_module(module_name)

        try:
            module = importlib.reload(self._loaded_modules[module_name])
            self._loaded_modules[module_name] = module
            return module
        except Exception:
            return None

    def get_loaded_modules(self) -> List[str]:
        """
        Get list of loaded module names.

        Returns:
            List of module names
        """
        return list(self._loaded_modules.keys())

    def unload_module(self, module_name: str) -> bool:
        """
        Unload a module.

        Args:
            module_name: Module to unload

        Returns:
            True if unloaded, False if not found
        """
        if module_name in self._loaded_modules:
            del self._loaded_modules[module_name]
            return True
        return False
