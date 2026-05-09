"""
Default configuration for Academic Toolbox.
Configuration reading priority: environment variable > config_private.py > config.py
"""

# API Keys
API_KEY = "your-api-key-here"

# Proxy settings
USE_PROXY = False
proxies = None

# Model settings
LLM_MODEL = "gpt-3.5-turbo"
AVAIL_LLM_MODELS = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
EMBEDDING_MODEL = "text-embedding-3-small"

# Web server settings
WEB_PORT = 8080
CONCURRENT_COUNT = 100
AUTHENTICATION = []

# UI settings
CHATBOT_HEIGHT = 1115
LAYOUT = "LEFT-RIGHT"
DARK_MODE = True
THEME = "Default"
AVAIL_THEMES = ["Default", "High-Contrast"]
AVAIL_FONTS = ["sans-serif"]

# System prompt
INIT_SYS_PROMPT = "Serve me as a writing and programming assistant."

# Timeouts and retries
TIMEOUT_SECONDS = 30
MAX_RETRY = 2

# Paths
PATH_LOGGING = "gpt_log"
PATH_PRIVATE_UPLOAD = "private_upload"

# Plugin settings
PLUGIN_HOT_RELOAD = False
DEFAULT_FN_GROUPS = ['chat', 'programming', 'academic']
NUM_CUSTOM_BASIC_BTN = 4

# Worker settings
DEFAULT_WORKER_NUM = 8

# Auto settings
AUTO_CLEAR_TXT = False
AUTO_OPEN_BROWSER = True
AUTO_CONTEXT_CLIP_ENABLE = False

# SSL settings
SSL_KEYFILE = ""
SSL_CERTFILE = ""

# Custom API key pattern (regex)
CUSTOM_API_KEY_PATTERN = ""

# API URL redirect
API_URL_REDIRECT = {}

# Azure settings
AZURE_ENDPOINT = ""
AZURE_API_KEY = ""
AZURE_ENGINE = ""
AZURE_CFG_ARRAY = {}

# When to use proxy
WHEN_TO_USE_PROXY = ["Connect_OpenAI", "Download_LLM"]

# Code highlight
CODE_HIGHLIGHT = True

# Add waifu decoration
ADD_WAIFU = False
