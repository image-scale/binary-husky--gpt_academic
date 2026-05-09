"""
Toolbox utilities module.
Provides various helper functions for file operations, time handling,
network proxy management, and chat history management.
"""
import os
import time
import traceback
import socket
import zipfile
from contextlib import closing
from typing import List, Optional

from .config_loader import get_conf

pj = os.path.join
DEFAULT_USER_NAME = "default_user"


def gen_time_str():
    """
    Generate a timestamp string.

    Returns:
        Formatted timestamp string in YYYY-MM-DD-HH-MM-SS format
    """
    return time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime())


def get_log_folder(user: str = None, plugin_name: str = "shared"):
    """
    Get the path to the logging folder, creating it if it doesn't exist.

    Args:
        user: Username for user-specific logs. Defaults to DEFAULT_USER_NAME.
        plugin_name: Plugin name for plugin-specific subfolder. None for user root.

    Returns:
        Path to the logging directory
    """
    if user is None:
        user = DEFAULT_USER_NAME

    path_logging = get_conf("PATH_LOGGING")
    if path_logging is None:
        path_logging = "gpt_log"

    if plugin_name is None:
        _dir = pj(path_logging, user)
    else:
        _dir = pj(path_logging, user, plugin_name)

    if not os.path.exists(_dir):
        os.makedirs(_dir, exist_ok=True)

    return _dir


def get_upload_folder(user: str = None, tag: str = None):
    """
    Get the path to the upload folder for a user.

    Args:
        user: Username. Defaults to DEFAULT_USER_NAME.
        tag: Optional tag for time-based subfolder.

    Returns:
        Path to the upload directory
    """
    path_upload = get_conf("PATH_PRIVATE_UPLOAD")
    if path_upload is None:
        path_upload = "private_upload"

    if user is None:
        user = DEFAULT_USER_NAME

    if tag is None or len(tag) == 0:
        target_path = pj(path_upload, user)
    else:
        target_path = pj(path_upload, user, tag)

    return target_path


def write_history_to_file(
    history: list,
    file_basename: str = None,
    file_fullname: str = None,
    auto_caption: bool = True
) -> str:
    """
    Write chat history to a markdown file.

    Args:
        history: List of chat messages (alternating user/assistant)
        file_basename: Basename for the file (without path)
        file_fullname: Full path to the file (takes precedence)
        auto_caption: If True, adds "## " prefix to user messages

    Returns:
        Absolute path to the created file
    """
    if file_fullname is None:
        if file_basename is not None:
            file_fullname = pj(get_log_folder(), file_basename)
        else:
            file_fullname = pj(get_log_folder(), f"GPT-Academic-{gen_time_str()}.md")

    os.makedirs(os.path.dirname(file_fullname), exist_ok=True)

    with open(file_fullname, "w", encoding="utf8") as f:
        f.write("# GPT-Academic Report\n")
        for i, content in enumerate(history):
            try:
                if not isinstance(content, str):
                    content = str(content)
            except:
                continue

            if i % 2 == 0 and auto_caption:
                f.write("## ")

            try:
                f.write(content)
            except:
                f.write(content.encode("utf-8", "ignore").decode())

            f.write("\n\n")

    return os.path.abspath(file_fullname)


def find_free_port() -> int:
    """
    Find an available port on the system.

    Returns:
        An available port number
    """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def find_recent_files(directory: str, seconds: int = 60) -> List[str]:
    """
    Find files created within a specified time window.

    Args:
        directory: Directory to search
        seconds: Time window in seconds (default: 60)

    Returns:
        List of file paths for recently created files
    """
    current_time = time.time()
    cutoff_time = current_time - seconds
    recent_files = []

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)
        return recent_files

    for filename in os.listdir(directory):
        file_path = pj(directory, filename)

        if file_path.endswith(".log"):
            continue

        if os.path.isdir(file_path):
            continue

        created_time = os.path.getmtime(file_path)
        if created_time >= cutoff_time:
            recent_files.append(file_path)

    return recent_files


def zip_folder(source_folder: str, dest_folder: str, zip_name: str) -> Optional[str]:
    """
    Compress a folder to a zip file.

    Args:
        source_folder: Path to the folder to compress
        dest_folder: Path to the destination folder
        zip_name: Name of the zip file to create

    Returns:
        Path to the created zip file, or None if failed
    """
    if not os.path.exists(source_folder):
        return None

    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder, exist_ok=True)

    zip_file = pj(dest_folder, zip_name)

    with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_folder):
            for filename in filenames:
                filepath = pj(foldername, filename)
                arcname = os.path.relpath(filepath, source_folder)
                zipf.write(filepath, arcname=arcname)

    return os.path.abspath(zip_file)


def trimmed_format_exc() -> str:
    """
    Get a traceback string with the current working directory path sanitized.

    Returns:
        Traceback string with paths replaced by "."
    """
    tb_str = traceback.format_exc()
    current_path = os.getcwd()
    return tb_str.replace(current_path, ".")


def trimmed_format_exc_markdown() -> str:
    """
    Get a traceback string formatted for markdown.

    Returns:
        Traceback wrapped in markdown code block
    """
    return '\n\n```\n' + trimmed_format_exc() + '```'


def regular_txt_to_markdown(text: str) -> str:
    """
    Convert plain text to markdown format.
    Adds double newlines for paragraph breaks.

    Args:
        text: Plain text to convert

    Returns:
        Markdown formatted text
    """
    if text is None:
        return ""
    text = text.replace("\n", "\n\n")
    text = text.replace("\n\n\n", "\n\n")
    text = text.replace("\n\n\n", "\n\n")
    return text


def clear_line_break(text: str) -> str:
    """
    Remove line breaks from text.

    Args:
        text: Text to process

    Returns:
        Text with line breaks replaced by spaces
    """
    if text is None:
        return None
    text = text.replace("\n", " ")
    text = text.replace("  ", " ")
    text = text.replace("  ", " ")
    return text


class DummyWith:
    """
    A dummy context manager that does nothing.
    Useful as a placeholder when a context manager is expected but no action is needed.
    """

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False


class ProxyNetworkActivate:
    """
    Context manager for temporarily activating proxy settings.
    Sets HTTP_PROXY and HTTPS_PROXY environment variables on enter,
    and clears them on exit.
    """

    def __init__(self, task: str = None):
        """
        Initialize the proxy activator.

        Args:
            task: Optional task name to check against WHEN_TO_USE_PROXY config
        """
        self.task = task
        self._original_env = {}

        if not task:
            self.valid = True
        else:
            when_to_use = get_conf("WHEN_TO_USE_PROXY")
            if when_to_use is None:
                when_to_use = []
            self.valid = task in when_to_use

    def __enter__(self):
        if not self.valid:
            return self

        proxies = get_conf("proxies")
        if proxies is None:
            return self

        # Save original values
        self._original_env = {
            "HTTP_PROXY": os.environ.get("HTTP_PROXY"),
            "HTTPS_PROXY": os.environ.get("HTTPS_PROXY"),
            "no_proxy": os.environ.get("no_proxy"),
        }

        # Remove no_proxy to enable proxy
        if "no_proxy" in os.environ:
            os.environ.pop("no_proxy")

        # Set proxy environment variables
        if isinstance(proxies, dict):
            if "http" in proxies:
                os.environ["HTTP_PROXY"] = proxies["http"]
            if "https" in proxies:
                os.environ["HTTPS_PROXY"] = proxies["https"]

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        # Restore original environment
        os.environ["no_proxy"] = "*"

        if "HTTP_PROXY" in os.environ:
            os.environ.pop("HTTP_PROXY")
        if "HTTPS_PROXY" in os.environ:
            os.environ.pop("HTTPS_PROXY")

        return False


def get_pictures_list(path: str) -> List[str]:
    """
    Get a list of image files in a directory.

    Args:
        path: Directory path to search

    Returns:
        List of image file paths (jpg, jpeg, png)
    """
    import glob

    if not os.path.exists(path):
        return []

    file_manifest = []
    file_manifest += glob.glob(f"{path}/**/*.jpg", recursive=True)
    file_manifest += glob.glob(f"{path}/**/*.jpeg", recursive=True)
    file_manifest += glob.glob(f"{path}/**/*.png", recursive=True)

    return file_manifest


def encode_image_base64(image_path: str) -> str:
    """
    Encode an image file to base64 string.

    Args:
        image_path: Path to the image file

    Returns:
        Base64 encoded string of the image
    """
    import base64

    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def check_packages(packages: List[str]) -> None:
    """
    Check if required packages are installed.

    Args:
        packages: List of package names to check

    Raises:
        ModuleNotFoundError: If any package is not found
    """
    import importlib.util

    for p in packages:
        spec = importlib.util.find_spec(p)
        if spec is None:
            raise ModuleNotFoundError(f"Package '{p}' not found")


def map_file_to_sha256(file_path: str) -> str:
    """
    Calculate SHA-256 hash of a file.

    Args:
        file_path: Path to the file

    Returns:
        SHA-256 hash string
    """
    import hashlib

    with open(file_path, 'rb') as f:
        content = f.read()

    return hashlib.sha256(content).hexdigest()


class Singleton:
    """
    Decorator for creating singleton classes.
    Ensures only one instance of a class exists.
    """

    def __init__(self, cls):
        self._cls = cls
        self._instance = None

    def __call__(self, *args, **kwargs):
        if self._instance is None:
            self._instance = self._cls(*args, **kwargs)
        return self._instance
