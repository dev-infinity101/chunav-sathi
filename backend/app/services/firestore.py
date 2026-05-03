from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any

from app.core.logging import get_logger

logger = get_logger(__name__)

_client: Any = None  # google.cloud.firestore_v1.AsyncClient


def _get_client() -> Any | None:
    global _client
    if _client is not None:
        return _client

    project_id = os.environ.get("PROJECT_ID", "")
    if not project_id:
        logger.warning("PROJECT_ID not set — Firestore client not initialised")
        return None

    try:
        from google.cloud import firestore  # type: ignore[import-untyped]

        _client = firestore.AsyncClient(project=project_id)
        logger.info("Firestore AsyncClient initialised for project %s", project_id)
        return _client
    except Exception as exc:
        logger.error("Failed to initialise Firestore client: %s", exc)
        return None


async def save_exchange(
    session_id: str,
    user_msg: str,
    assistant_msg: str,
    lang: str,
    level: str | None,
    citations: list[str],
) -> None:
    client = _get_client()
    if client is None:
        return

    try:
        doc_ref = (
            client.collection("sessions")
            .document(session_id)
            .collection("exchanges")
            .document()
        )
        await doc_ref.set(
            {
                "user_msg": user_msg,
                "assistant_msg": assistant_msg,
                "lang": lang,
                "level": level,
                "citations": citations,
                "timestamp": datetime.now(timezone.utc),
            }
        )
    except Exception as exc:
        logger.error("Firestore save_exchange error (session=%s): %s", session_id, exc)


async def get_session_history(session_id: str, limit: int = 10) -> list[dict]:  # type: ignore[type-arg]
    client = _get_client()
    if client is None:
        return []

    try:
        from google.cloud import firestore  # type: ignore[import-untyped]

        ref = (
            client.collection("sessions")
            .document(session_id)
            .collection("exchanges")
            .order_by("timestamp", direction=firestore.Query.DESCENDING)
            .limit(limit)
        )
        docs = await ref.get()
        history = []
        for doc in reversed(docs):
            data = doc.to_dict() or {}
            history.append({"role": "user", "text": data.get("user_msg", "")})
            history.append({"role": "model", "text": data.get("assistant_msg", "")})
        return history
    except Exception as exc:
        logger.error("Firestore get_session_history error (session=%s): %s", session_id, exc)
        return []
