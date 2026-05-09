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
- [ ] markdown_to_html converts basic markdown (headers, lists, bold, italic) to HTML
- [ ] Code blocks are converted with proper syntax highlighting
- [ ] LaTeX equations in $...$ format are detected and converted to MathML
- [ ] Display equations in $$...$$ format are also supported
- [ ] Fix indent for markdown lists to ensure proper nesting
- [ ] Close unclosed code blocks during streaming (incomplete output)
- [ ] is_equation detects presence of math formulas in text
- [ ] Already-converted HTML passes through unchanged
