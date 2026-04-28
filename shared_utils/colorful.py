# Colored console output functions
# Uses ANSI escape codes for terminal coloring

# ANSI color codes
RED = "\033[91m"
GREEN = "\033[92m"
BLUE = "\033[94m"
RESET = "\033[0m"


def sprint红(*args):
    """Return red colored string."""
    text = " ".join(str(arg) for arg in args)
    return f"{RED}{text}{RESET}"


def sprint绿(*args):
    """Return green colored string."""
    text = " ".join(str(arg) for arg in args)
    return f"{GREEN}{text}{RESET}"


def sprint蓝(*args):
    """Return blue colored string."""
    text = " ".join(str(arg) for arg in args)
    return f"{BLUE}{text}{RESET}"


def print红(*args, **kwargs):
    """Print in red color."""
    text = sprint红(*args)
    print(text, **kwargs)


def print绿(*args, **kwargs):
    """Print in green color."""
    text = sprint绿(*args)
    print(text, **kwargs)


def print蓝(*args, **kwargs):
    """Print in blue color."""
    text = sprint蓝(*args)
    print(text, **kwargs)
