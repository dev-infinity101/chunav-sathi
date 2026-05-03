from __future__ import annotations

import os
from functools import lru_cache

from app.core.logging import get_logger

logger = get_logger(__name__)


@lru_cache(maxsize=32)
def get_secret(name: str) -> str:
    """
    Return secret value.
    Priority:
      1. Environment variable (name uppercased, hyphens→underscores)
      2. Google Secret Manager (requires PROJECT_ID env var)
      3. Empty string (logs a warning)
    """
    env_key = name.upper().replace("-", "_")
    env_val = os.environ.get(env_key, "")
    if env_val:
        return env_val

    project_id = os.environ.get("PROJECT_ID", "")
    if not project_id:
        logger.warning("Secret '%s' not in env and PROJECT_ID not set", name)
        return ""

    try:
        from google.cloud import secretmanager  # type: ignore[import-untyped]

        client = secretmanager.SecretManagerServiceClient()
        secret_path = f"projects/{project_id}/secrets/{name}/versions/latest"
        response = client.access_secret_version(request={"name": secret_path})
        value = response.payload.data.decode("utf-8")
        logger.info("Fetched secret '%s' from Secret Manager", name)
        return value
    except Exception as exc:
        logger.error("Failed to fetch secret '%s': %s", name, exc)
        return ""
