# Acceptance Criteria

## Task 1: Configuration Management System

### Acceptance Criteria
- [x] get_conf("API_KEY") returns the API key value from config when no env var is set
- [x] get_conf("WEB_PORT") returns integer value 8080 when config specifies 8080
- [x] get_conf with multiple args returns tuple of values: get_conf("A", "B") returns (val_a, val_b)
- [x] Environment variable GPT_ACADEMIC_API_KEY overrides config file value
- [x] Environment variable without prefix (API_KEY) also works as override
- [x] Boolean config "USE_PROXY" returns True/False correctly from env var "True"/"False"
- [x] List config from env var like '["a","b"]' is properly evaluated to Python list
- [x] Dict config from env var like '{"key":"val"}' is properly evaluated to Python dict
- [x] set_conf("KEY", "value") updates the configuration and future get_conf returns new value
- [x] set_multi_conf({"A": 1, "B": 2}) sets multiple configs at once
- [x] read_single_conf_with_lru_cache caches results for repeated reads
- [x] Cache is cleared when set_conf is called

## Task 2: API Key Pattern Validation

### Acceptance Criteria
- [x] is_openai_api_key("sk-" + 48 chars) returns True for valid OpenAI key
- [x] is_openai_api_key("sk-proj-" + 124/156 chars) returns True for project keys
- [x] is_openai_api_key("sess-" + 40 chars) returns True for session keys
- [x] is_openai_api_key("invalid") returns False for invalid key
- [x] is_azure_api_key with 32 alphanumeric chars returns True
- [x] is_api2d_key("fk" + 6 chars + "-" + 32 chars) returns True
- [x] is_any_api_key returns True for any valid key type
- [x] is_any_api_key returns True for comma-separated multiple keys
- [x] select_api_key selects appropriate key type for "gpt-3.5-turbo" model (OpenAI)
- [x] select_api_key selects appropriate key type for "azure-gpt-4" model (Azure)
- [x] select_api_key raises RuntimeError when no matching key is found
- [x] what_keys returns a summary string counting keys by type

## Task 3: Text Masking Utilities

### Acceptance Criteria
- [x] build_masked_string creates a string with both English and Chinese versions
- [x] apply_mask("show_english") extracts the English version from masked string
- [x] apply_mask("show_chinese") extracts the Chinese version from masked string
- [x] Language detection identifies English text correctly
- [x] Language detection identifies Chinese text correctly
- [x] apply_mask_langbased auto-selects based on detected language of reference text
- [x] Non-masked strings pass through unchanged
- [x] Empty or None inputs are handled gracefully

## Task 4: Colorful Logging Utilities

### Acceptance Criteria
- [x] log_red("message") prints message in red color
- [x] log_green("message") prints message in green color
- [x] log_blue("message") prints message in blue color
- [x] log_yellow("message") prints message in yellow color
- [x] Multiple arguments are joined with space separator
- [x] Non-string arguments are converted to strings
- [x] Print function fallback works when colorama is not available

## Task 5: Markdown-to-HTML Conversion

### Acceptance Criteria
- [x] markdown_to_html converts basic markdown (headers, lists, bold, italic) to HTML
- [x] Code blocks are converted with proper syntax highlighting
- [x] LaTeX equations in $...$ format are detected and converted to MathML
- [x] Display equations in $$...$$ format are also supported
- [x] Fix indent for markdown lists to ensure proper nesting
- [x] Close unclosed code blocks during streaming (incomplete output)
- [x] is_equation detects presence of math formulas in text
- [x] Already-converted HTML passes through unchanged

## Task 6: Core Text Processing Functions

### Acceptance Criteria
- [x] get_core_functions() returns a dictionary of function definitions
- [x] Each function definition has at least "Prefix" and "Suffix" keys
- [x] Academic polishing function uses bilingual masked strings (English/Chinese variants)
- [x] Grammar checking function includes example format showing corrections table
- [x] Translation functions exist for Chinese-to-English and English-to-Chinese
- [x] Code explanation function wraps input in code block delimiters
- [x] Mind map function generates mermaid flowchart prompt
- [x] handle_core_functionality applies prefix and suffix to user inputs
- [x] PreProcess function is called when defined in function config
- [x] AutoClearHistory option clears history when True

## Task 7: Main Toolbox Utilities

### Acceptance Criteria
- [x] write_history_to_file writes chat history to markdown file with proper formatting
- [x] gen_time_str generates timestamp string in YYYY-MM-DD-HH-MM-SS format
- [x] find_free_port returns an available port number
- [x] find_recent_files finds files created within a specified time window
- [x] zip_folder compresses directory contents to a zip file
- [x] ProxyNetworkActivate context manager sets/clears proxy environment variables
- [x] DummyWith context manager does nothing (passthrough)
- [x] trimmed_format_exc returns traceback with paths sanitized
- [x] regular_txt_to_markdown converts plain text to markdown format
- [x] get_log_folder returns path to logging directory, creating it if needed

## Task 8: Basic LLM Bridge Interface

### Acceptance Criteria
- [x] Model registry stores model configurations with max_token, endpoint, and tokenizer type
- [x] get_model_info returns model information for registered models
- [x] get_available_models lists all registered model names
- [x] Token counting works for text and message lists
- [x] build_messages constructs message list from user input, history, and system prompt
- [x] build_payload creates API request payload with model-specific handling
- [x] build_headers generates proper headers for OpenAI and Azure APIs
- [x] verify_endpoint validates endpoint URLs
- [x] parse_stream_response extracts content from streamed chunks
- [x] LLMBridge class provides predict interface for API calls

## Task 9: Plugin System with Hot Reload

### Acceptance Criteria
- [x] register_plugin registers a function with metadata (group, color, info)
- [x] get_plugin retrieves a registered plugin by name
- [x] get_all_plugins returns all registered plugins
- [x] get_plugins_by_group filters plugins by group membership
- [x] dispatch_plugin calls the registered function with arguments
- [x] hot_reload decorator enables function reloading without restart
- [x] plugin decorator provides convenient registration syntax
- [x] load_plugins_from_dict loads plugins from legacy dictionary format
- [x] match_group checks if plugin belongs to selected groups
- [x] PluginManager handles module loading and reloading

## Task 10: Main Integration Module

### Acceptance Criteria
- [x] AcademicConfig loads settings from configuration files
- [x] AcademicToolbox provides unified access to all modules
- [x] create_toolbox creates configured toolbox instance
- [x] get_system_info returns system status dictionary
- [x] chat method sends messages and returns responses (via LLMBridge)
- [x] apply_core_function applies academic processing functions
- [x] format_markdown converts markdown to HTML
- [x] write_history saves conversation to file
- [x] Convenience functions (polish_text, check_grammar, translate_text, explain_code)
- [x] Plugin registration and dispatch through toolbox interface
