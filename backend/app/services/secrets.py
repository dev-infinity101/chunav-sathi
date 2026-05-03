import os
from functools import lru_cache

# Full implementation: Prompt 4


@lru_cache(maxsize=32)
def get_secret(name: str) -> str:
    """Returns env var if set, otherwise fetches from Secret Manager."""
    env_val = os.environ.get(name.upper().replace("-", "_"), "")
    if env_val:
        return env_val
    # Secret Manager fetch implemented in Prompt 4
    return ""
