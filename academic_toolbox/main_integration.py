"""
Main integration module that ties together all academic toolbox components.
Provides a unified interface for configuration, LLM access, plugins, and utilities.
"""
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass

# Import all modules
from .config_loader import get_conf, set_conf, set_multi_conf
from .key_pattern_manager import (
    is_openai_api_key,
    is_azure_api_key,
    is_any_api_key,
    select_api_key,
    what_keys,
)
from .text_mask import (
    build_masked_string,
    apply_mask,
    apply_mask_langbased,
    detect_language,
)
from .colorful import log_red, log_green, log_blue, log_yellow
from .markdown_format import (
    markdown_to_html,
    is_equation,
    fix_markdown_indent,
    close_up_code_segment,
    format_chat_output,
)
from .core_functional import (
    get_core_functions,
    handle_core_functionality,
    get_function_names,
)
from .toolbox import (
    gen_time_str,
    get_log_folder,
    get_upload_folder,
    write_history_to_file,
    find_free_port,
    find_recent_files,
    zip_folder,
    trimmed_format_exc,
    ProxyNetworkActivate,
    DummyWith,
)
from .llm_bridge import (
    ModelInfo,
    TokenCounter,
    LLMBridge,
    get_model_info,
    get_available_models,
    get_max_token,
    get_token_count,
    build_messages,
    build_payload,
)
from .plugin_system import (
    PluginInfo,
    register_plugin,
    get_plugin,
    get_all_plugins,
    get_plugins_by_group,
    dispatch_plugin,
    hot_reload,
    plugin,
    load_plugins_from_dict,
    PluginManager,
)


@dataclass
class AcademicConfig:
    """Configuration container for the academic toolbox."""
    api_key: str = ""
    llm_model: str = "gpt-3.5-turbo"
    web_port: int = 8080
    use_proxy: bool = False
    proxies: Optional[Dict[str, str]] = None
    path_logging: str = "gpt_log"
    path_upload: str = "private_upload"

    @classmethod
    def from_config(cls) -> "AcademicConfig":
        """Create config from configuration files."""
        return cls(
            api_key=get_conf("API_KEY") or "",
            llm_model=get_conf("LLM_MODEL") or "gpt-3.5-turbo",
            web_port=get_conf("WEB_PORT") or 8080,
            use_proxy=get_conf("USE_PROXY") or False,
            proxies=get_conf("proxies"),
            path_logging=get_conf("PATH_LOGGING") or "gpt_log",
            path_upload=get_conf("PATH_PRIVATE_UPLOAD") or "private_upload",
        )


class AcademicToolbox:
    """
    Main integration class providing unified access to all toolbox functionality.
    """

    def __init__(self, config: Optional[AcademicConfig] = None):
        """
        Initialize the academic toolbox.

        Args:
            config: Configuration object. If None, loads from config files.
        """
        if config is None:
            config = AcademicConfig.from_config()
        self.config = config
        self._llm_bridge: Optional[LLMBridge] = None
        self._plugin_manager = PluginManager()

    @property
    def llm(self) -> LLMBridge:
        """Get or create the LLM bridge."""
        if self._llm_bridge is None:
            self._llm_bridge = LLMBridge(
                api_key=self.config.api_key,
                model_name=self.config.llm_model,
                proxies=self.config.proxies if self.config.use_proxy else None,
            )
        return self._llm_bridge

    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key and recreate the LLM bridge.

        Args:
            api_key: New API key
        """
        self.config.api_key = api_key
        self._llm_bridge = None

    def set_model(self, model_name: str) -> None:
        """
        Set the LLM model and recreate the bridge.

        Args:
            model_name: New model name
        """
        self.config.llm_model = model_name
        self._llm_bridge = None

    def validate_api_key(self) -> bool:
        """
        Validate the current API key.

        Returns:
            True if API key appears valid
        """
        return is_any_api_key(self.config.api_key)

    def get_key_summary(self) -> str:
        """
        Get a summary of configured API keys.

        Returns:
            Summary string describing available keys
        """
        return what_keys(self.config.api_key)

    def chat(
        self,
        message: str,
        history: List[str] = None,
        system_prompt: str = "",
    ) -> str:
        """
        Send a chat message and get a response.

        Args:
            message: User message
            history: Previous conversation history
            system_prompt: System prompt

        Returns:
            Assistant response
        """
        return self.llm.predict(
            user_input=message,
            history=history or [],
            system_prompt=system_prompt,
        )

    def apply_core_function(
        self,
        func_name: str,
        user_input: str,
        history: List[str] = None,
    ) -> tuple:
        """
        Apply a core function (academic polish, grammar check, etc.)

        Args:
            func_name: Name of the core function
            user_input: User input text
            history: Conversation history

        Returns:
            Tuple of (transformed_input, updated_history)
        """
        return handle_core_functionality(
            func_name, user_input, history or []
        )

    def list_core_functions(self, visible_only: bool = True) -> List[str]:
        """
        List available core functions.

        Args:
            visible_only: Only return visible functions

        Returns:
            List of function names
        """
        return get_function_names(visible_only)

    def format_markdown(self, text: str) -> str:
        """
        Convert markdown text to HTML.

        Args:
            text: Markdown text

        Returns:
            HTML string
        """
        return markdown_to_html(text)

    def write_history(
        self,
        history: List[str],
        filename: str = None,
    ) -> str:
        """
        Write conversation history to a file.

        Args:
            history: Conversation history
            filename: Optional filename

        Returns:
            Path to the created file
        """
        return write_history_to_file(history, file_basename=filename)

    def register_plugin(
        self,
        name: str,
        func: Callable,
        **kwargs,
    ) -> PluginInfo:
        """
        Register a plugin function.

        Args:
            name: Plugin name
            func: Plugin function
            **kwargs: Additional plugin options

        Returns:
            PluginInfo object
        """
        return register_plugin(name, func, **kwargs)

    def call_plugin(self, name: str, *args, **kwargs) -> Any:
        """
        Call a registered plugin.

        Args:
            name: Plugin name
            *args: Positional arguments
            **kwargs: Keyword arguments

        Returns:
            Plugin result
        """
        return dispatch_plugin(name, *args, **kwargs)

    def list_plugins(self, group: str = None) -> List[PluginInfo]:
        """
        List available plugins.

        Args:
            group: Optional group filter

        Returns:
            List of plugins
        """
        if group:
            return get_plugins_by_group(group)
        return list(get_all_plugins().values())

    def count_tokens(self, text: str) -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count

        Returns:
            Token count
        """
        model_type = "gpt4" if "gpt-4" in self.config.llm_model else "gpt35"
        return get_token_count(text, model_type)

    def detect_text_language(self, text: str) -> str:
        """
        Detect the language of text.

        Args:
            text: Text to analyze

        Returns:
            Language code ("en", "zh", or "unknown")
        """
        return detect_language(text)


def create_toolbox(
    api_key: str = None,
    model: str = None,
) -> AcademicToolbox:
    """
    Create an AcademicToolbox instance with optional overrides.

    Args:
        api_key: Optional API key override
        model: Optional model name override

    Returns:
        Configured AcademicToolbox instance
    """
    config = AcademicConfig.from_config()
    if api_key:
        config.api_key = api_key
    if model:
        config.llm_model = model
    return AcademicToolbox(config)


def get_system_info() -> Dict[str, Any]:
    """
    Get system information and configuration status.

    Returns:
        Dictionary with system information
    """
    config = AcademicConfig.from_config()
    return {
        "version": "1.0.0",
        "llm_model": config.llm_model,
        "web_port": config.web_port,
        "use_proxy": config.use_proxy,
        "api_key_valid": is_any_api_key(config.api_key),
        "available_models": get_available_models(),
        "core_functions": get_function_names(),
        "plugins_count": len(get_all_plugins()),
        "log_folder": get_log_folder(),
    }


def initialize_logging(log_folder: str = None) -> str:
    """
    Initialize logging to the specified folder.

    Args:
        log_folder: Optional log folder override

    Returns:
        Path to the log folder
    """
    if log_folder is None:
        log_folder = get_conf("PATH_LOGGING") or "gpt_log"
    folder = get_log_folder()
    log_green(f"Logging initialized at: {folder}")
    return folder


def quick_chat(
    message: str,
    api_key: str = None,
    model: str = "gpt-3.5-turbo",
) -> str:
    """
    Quick one-shot chat without maintaining a toolbox instance.

    Args:
        message: User message
        api_key: API key (uses config if not provided)
        model: Model name

    Returns:
        Assistant response
    """
    if api_key is None:
        api_key = get_conf("API_KEY")

    bridge = LLMBridge(api_key=api_key, model_name=model)
    return bridge.predict(message)


# Module-level convenience functions
def polish_text(text: str, language: str = None) -> tuple:
    """
    Apply academic polishing to text.

    Args:
        text: Text to polish
        language: Optional language hint

    Returns:
        Tuple of (polished_prompt, history)
    """
    return handle_core_functionality("Academic Polish", text, [])


def check_grammar(text: str) -> tuple:
    """
    Check grammar in text.

    Args:
        text: Text to check

    Returns:
        Tuple of (grammar_check_prompt, history)
    """
    return handle_core_functionality("Grammar Check", text, [])


def translate_text(text: str, direction: str = "en_to_zh") -> tuple:
    """
    Translate text between English and Chinese.

    Args:
        text: Text to translate
        direction: "en_to_zh" or "zh_to_en"

    Returns:
        Tuple of (translation_prompt, history)
    """
    if direction == "zh_to_en":
        return handle_core_functionality("Chinese to English", text, [])
    else:
        return handle_core_functionality("English to Chinese", text, [])


def explain_code(code: str) -> tuple:
    """
    Generate code explanation prompt.

    Args:
        code: Code to explain

    Returns:
        Tuple of (explanation_prompt, history)
    """
    return handle_core_functionality("Explain Code", code, [])
