# Acceptance Criteria

## Task 1: Configuration Management System

### Acceptance Criteria
- [ ] get_conf("API_KEY") returns the API key value from config when no env var is set
- [ ] get_conf("WEB_PORT") returns integer value 8080 when config specifies 8080
- [ ] get_conf with multiple args returns tuple of values: get_conf("A", "B") returns (val_a, val_b)
- [ ] Environment variable GPT_ACADEMIC_API_KEY overrides config file value
- [ ] Environment variable without prefix (API_KEY) also works as override
- [ ] Boolean config "USE_PROXY" returns True/False correctly from env var "True"/"False"
- [ ] List config from env var like '["a","b"]' is properly evaluated to Python list
- [ ] Dict config from env var like '{"key":"val"}' is properly evaluated to Python dict
- [ ] set_conf("KEY", "value") updates the configuration and future get_conf returns new value
- [ ] set_multi_conf({"A": 1, "B": 2}) sets multiple configs at once
- [ ] read_single_conf_with_lru_cache caches results for repeated reads
- [ ] Cache is cleared when set_conf is called
