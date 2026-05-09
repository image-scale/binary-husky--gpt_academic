"""Tests for the plugin system module."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from academic_toolbox.plugin_system import (
    PluginInfo,
    hot_reload,
    register_plugin,
    unregister_plugin,
    get_plugin,
    get_all_plugins,
    get_plugins_by_group,
    get_all_groups,
    get_button_plugins,
    get_dropdown_plugins,
    dispatch_plugin,
    clear_plugins,
    plugin,
    load_plugins_from_dict,
    to_legacy_format,
    match_group,
    PluginManager,
)


class TestPluginInfo(unittest.TestCase):
    """Test cases for PluginInfo dataclass."""

    def test_create_plugin_info(self):
        """Test creating PluginInfo."""
        def dummy_func():
            pass

        info = PluginInfo(
            name="Test Plugin",
            function=dummy_func,
            group="test",
        )
        self.assertEqual(info.name, "Test Plugin")
        self.assertEqual(info.group, "test")
        self.assertTrue(info.as_button)

    def test_plugin_info_defaults(self):
        """Test PluginInfo defaults."""
        def dummy_func():
            pass

        info = PluginInfo(name="Test", function=dummy_func)
        self.assertEqual(info.color, "secondary")
        self.assertTrue(info.visible)
        self.assertFalse(info.advanced_args)


class TestRegisterPlugin(unittest.TestCase):
    """Test cases for plugin registration."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_register_basic_plugin(self):
        """Test registering a basic plugin."""
        def my_plugin():
            return "result"

        info = register_plugin("My Plugin", my_plugin)
        self.assertEqual(info.name, "My Plugin")
        self.assertEqual(info.function, my_plugin)

    def test_register_plugin_with_options(self):
        """Test registering plugin with all options."""
        def my_plugin():
            pass

        info = register_plugin(
            name="Advanced Plugin",
            function=my_plugin,
            group="tools|utilities",
            color="primary",
            as_button=False,
            info="Does advanced things",
            advanced_args=True,
            args_reminder="Use --flag for feature",
        )
        self.assertEqual(info.group, "tools|utilities")
        self.assertEqual(info.color, "primary")
        self.assertFalse(info.as_button)
        self.assertTrue(info.advanced_args)

    def test_get_registered_plugin(self):
        """Test getting a registered plugin."""
        def my_plugin():
            pass

        register_plugin("Test", my_plugin)
        retrieved = get_plugin("Test")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.name, "Test")

    def test_get_nonexistent_plugin(self):
        """Test getting a nonexistent plugin."""
        result = get_plugin("Nonexistent")
        self.assertIsNone(result)


class TestUnregisterPlugin(unittest.TestCase):
    """Test cases for plugin unregistration."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_unregister_existing_plugin(self):
        """Test unregistering an existing plugin."""
        def my_plugin():
            pass

        register_plugin("Test", my_plugin)
        result = unregister_plugin("Test")
        self.assertTrue(result)
        self.assertIsNone(get_plugin("Test"))

    def test_unregister_nonexistent_plugin(self):
        """Test unregistering a nonexistent plugin."""
        result = unregister_plugin("Nonexistent")
        self.assertFalse(result)


class TestGetAllPlugins(unittest.TestCase):
    """Test cases for getting all plugins."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_get_all_plugins_empty(self):
        """Test getting all plugins when empty."""
        plugins = get_all_plugins()
        self.assertEqual(len(plugins), 0)

    def test_get_all_plugins_multiple(self):
        """Test getting all plugins with multiple registered."""
        register_plugin("Plugin 1", lambda: None)
        register_plugin("Plugin 2", lambda: None)
        register_plugin("Plugin 3", lambda: None)

        plugins = get_all_plugins()
        self.assertEqual(len(plugins), 3)
        self.assertIn("Plugin 1", plugins)
        self.assertIn("Plugin 2", plugins)


class TestGetPluginsByGroup(unittest.TestCase):
    """Test cases for getting plugins by group."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_get_plugins_single_group(self):
        """Test getting plugins from a single group."""
        register_plugin("P1", lambda: None, group="coding")
        register_plugin("P2", lambda: None, group="coding")
        register_plugin("P3", lambda: None, group="academic")

        coding_plugins = get_plugins_by_group("coding")
        self.assertEqual(len(coding_plugins), 2)

    def test_get_plugins_multi_group(self):
        """Test getting plugins with multi-group membership."""
        register_plugin("P1", lambda: None, group="coding|academic")
        register_plugin("P2", lambda: None, group="academic")

        academic_plugins = get_plugins_by_group("academic")
        self.assertEqual(len(academic_plugins), 2)


class TestGetAllGroups(unittest.TestCase):
    """Test cases for getting all groups."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_get_all_groups(self):
        """Test getting all groups."""
        register_plugin("P1", lambda: None, group="coding")
        register_plugin("P2", lambda: None, group="academic")
        register_plugin("P3", lambda: None, group="coding|tools")

        groups = get_all_groups()
        self.assertIn("coding", groups)
        self.assertIn("academic", groups)
        self.assertIn("tools", groups)


class TestButtonAndDropdownPlugins(unittest.TestCase):
    """Test cases for button and dropdown plugin filters."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_get_button_plugins(self):
        """Test getting button plugins."""
        register_plugin("Button", lambda: None, as_button=True)
        register_plugin("Dropdown", lambda: None, as_button=False)

        buttons = get_button_plugins()
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].name, "Button")

    def test_get_dropdown_plugins(self):
        """Test getting dropdown plugins."""
        register_plugin("Button", lambda: None, as_button=True)
        register_plugin("Dropdown", lambda: None, as_button=False)

        dropdowns = get_dropdown_plugins()
        self.assertEqual(len(dropdowns), 1)
        self.assertEqual(dropdowns[0].name, "Dropdown")

    def test_invisible_plugins_excluded(self):
        """Test that invisible plugins are excluded."""
        register_plugin("Visible", lambda: None, as_button=True, visible=True)
        register_plugin("Hidden", lambda: None, as_button=True, visible=False)

        buttons = get_button_plugins()
        self.assertEqual(len(buttons), 1)
        self.assertEqual(buttons[0].name, "Visible")


class TestDispatchPlugin(unittest.TestCase):
    """Test cases for plugin dispatch."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_dispatch_basic(self):
        """Test dispatching a basic plugin."""
        def add(a, b):
            return a + b

        register_plugin("Add", add)
        result = dispatch_plugin("Add", 2, 3)
        self.assertEqual(result, 5)

    def test_dispatch_with_kwargs(self):
        """Test dispatching with keyword arguments."""
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"

        register_plugin("Greet", greet)
        result = dispatch_plugin("Greet", "World", greeting="Hi")
        self.assertEqual(result, "Hi, World!")

    def test_dispatch_nonexistent_raises(self):
        """Test that dispatching nonexistent plugin raises KeyError."""
        with self.assertRaises(KeyError):
            dispatch_plugin("Nonexistent")


class TestPluginDecorator(unittest.TestCase):
    """Test cases for the plugin decorator."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_decorator_registers_plugin(self):
        """Test that decorator registers the plugin."""
        @plugin(name="Decorated Plugin", info="A test plugin")
        def my_func():
            return "decorated"

        registered = get_plugin("Decorated Plugin")
        self.assertIsNotNone(registered)
        self.assertEqual(registered.info, "A test plugin")

    def test_decorator_default_name(self):
        """Test decorator uses function name as default."""
        @plugin()
        def auto_named_plugin():
            pass

        registered = get_plugin("auto_named_plugin")
        self.assertIsNotNone(registered)

    def test_decorator_preserves_function(self):
        """Test decorator preserves function behavior."""
        @plugin(name="Working")
        def working_plugin(x):
            return x * 2

        result = working_plugin(5)
        self.assertEqual(result, 10)


class TestLoadPluginsFromDict(unittest.TestCase):
    """Test cases for loading plugins from dictionary."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_load_from_dict(self):
        """Test loading plugins from dictionary."""
        plugins_dict = {
            "Plugin A": {
                "Function": lambda: "A",
                "Group": "test",
                "Color": "primary",
            },
            "Plugin B": {
                "Function": lambda: "B",
                "Info": "Plugin B info",
            },
        }

        loaded = load_plugins_from_dict(plugins_dict)
        self.assertEqual(len(loaded), 2)

        plugin_a = get_plugin("Plugin A")
        self.assertIsNotNone(plugin_a)
        self.assertEqual(plugin_a.color, "primary")

    def test_skip_missing_function(self):
        """Test that plugins without Function are skipped."""
        plugins_dict = {
            "Valid": {"Function": lambda: None},
            "Invalid": {"Info": "No function"},
        }

        loaded = load_plugins_from_dict(plugins_dict)
        self.assertEqual(len(loaded), 1)


class TestToLegacyFormat(unittest.TestCase):
    """Test cases for exporting to legacy format."""

    def setUp(self):
        """Clear plugins before each test."""
        clear_plugins()

    def tearDown(self):
        """Clear plugins after each test."""
        clear_plugins()

    def test_export_to_legacy(self):
        """Test exporting to legacy dictionary format."""
        register_plugin(
            "Test Plugin",
            lambda: None,
            group="test",
            color="stop",
            info="Test info",
        )

        legacy = to_legacy_format()
        self.assertIn("Test Plugin", legacy)
        self.assertEqual(legacy["Test Plugin"]["Group"], "test")
        self.assertEqual(legacy["Test Plugin"]["Color"], "stop")


class TestMatchGroup(unittest.TestCase):
    """Test cases for group matching."""

    def test_single_group_match(self):
        """Test matching a single group."""
        self.assertTrue(match_group("coding", ["coding"]))
        self.assertFalse(match_group("coding", ["academic"]))

    def test_multi_group_match(self):
        """Test matching multiple groups."""
        self.assertTrue(match_group("coding|academic", ["academic"]))
        self.assertTrue(match_group("coding|academic", ["coding"]))
        self.assertFalse(match_group("coding|academic", ["tools"]))


class TestHotReload(unittest.TestCase):
    """Test cases for hot reload decorator."""

    def test_hot_reload_preserves_function(self):
        """Test that hot_reload preserves function behavior."""
        @hot_reload
        def test_func(x):
            return x + 1

        result = test_func(5)
        self.assertEqual(result, 6)


class TestPluginManager(unittest.TestCase):
    """Test cases for PluginManager class."""

    def test_create_manager(self):
        """Test creating a PluginManager."""
        manager = PluginManager()
        self.assertEqual(len(manager.get_loaded_modules()), 0)

    def test_load_builtin_module(self):
        """Test loading a builtin module."""
        manager = PluginManager()
        module = manager.load_plugin_module("os")
        self.assertIsNotNone(module)
        self.assertIn("os", manager.get_loaded_modules())

    def test_reload_module(self):
        """Test reloading a module."""
        manager = PluginManager()
        manager.load_plugin_module("os")
        reloaded = manager.reload_plugin_module("os")
        self.assertIsNotNone(reloaded)

    def test_unload_module(self):
        """Test unloading a module."""
        manager = PluginManager()
        manager.load_plugin_module("os")
        result = manager.unload_module("os")
        self.assertTrue(result)
        self.assertNotIn("os", manager.get_loaded_modules())

    def test_unload_nonexistent(self):
        """Test unloading a nonexistent module."""
        manager = PluginManager()
        result = manager.unload_module("nonexistent")
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
