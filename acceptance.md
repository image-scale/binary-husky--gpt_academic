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
- [ ] is_openai_api_key("sk-" + 48 chars) returns True for valid OpenAI key
- [ ] is_openai_api_key("sk-proj-" + 124/156 chars) returns True for project keys
- [ ] is_openai_api_key("sess-" + 40 chars) returns True for session keys
- [ ] is_openai_api_key("invalid") returns False for invalid key
- [ ] is_azure_api_key with 32 alphanumeric chars returns True
- [ ] is_api2d_key("fk" + 6 chars + "-" + 32 chars) returns True
- [ ] is_any_api_key returns True for any valid key type
- [ ] is_any_api_key returns True for comma-separated multiple keys
- [ ] select_api_key selects appropriate key type for "gpt-3.5-turbo" model (OpenAI)
- [ ] select_api_key selects appropriate key type for "azure-gpt-4" model (Azure)
- [ ] select_api_key raises RuntimeError when no matching key is found
- [ ] what_keys returns a summary string counting keys by type
