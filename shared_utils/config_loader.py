# Configuration loading functions
from functools import lru_cache

@lru_cache
def read_single_conf_with_lru_cache(key):
    raise NotImplementedError

@lru_cache
def get_conf(*keys):
    raise NotImplementedError
