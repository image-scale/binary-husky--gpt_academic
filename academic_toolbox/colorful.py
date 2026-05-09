"""
Colorful logging utilities module.
Provides styled console output with different colors for various log levels.
Uses colorama for cross-platform color support.
"""
import sys

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False


def _format_message(*args):
    """Format multiple arguments into a single message string."""
    return ' '.join(str(arg) for arg in args)


def log_red(*args):
    """
    Print a message in bright red color.
    Used for errors, warnings, or important alerts.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTRED_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[RED] {message}")


def log_green(*args):
    """
    Print a message in bright green color.
    Used for success messages and confirmations.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTGREEN_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[GREEN] {message}")


def log_blue(*args):
    """
    Print a message in bright blue color.
    Used for informational messages.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTBLUE_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[BLUE] {message}")


def log_yellow(*args):
    """
    Print a message in bright yellow color.
    Used for warnings and attention-needed messages.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTYELLOW_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[YELLOW] {message}")


def log_cyan(*args):
    """
    Print a message in bright cyan color.
    Used for special informational messages.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTCYAN_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[CYAN] {message}")


def log_magenta(*args):
    """
    Print a message in bright magenta color.
    Used for special highlights.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTMAGENTA_EX}{message}{Style.RESET_ALL}")
    else:
        print(f"[MAGENTA] {message}")


def log_white(*args):
    """
    Print a message in bright white color.
    Used for standard output with emphasis.

    Args:
        *args: Message parts to print (will be joined with spaces)
    """
    message = _format_message(*args)
    if COLORAMA_AVAILABLE:
        print(f"{Fore.LIGHTWHITE_EX}{message}{Style.RESET_ALL}")
    else:
        print(message)


# Chinese aliases for compatibility with original project
log_bright_red = log_red
log_bright_green = log_green
log_bright_blue = log_blue
log_bright_yellow = log_yellow


def is_colorama_available():
    """Check if colorama is available for colored output."""
    return COLORAMA_AVAILABLE
