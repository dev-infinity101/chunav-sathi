from __future__ import annotations

import os

import numpy as np

from app.core.logging import get_logger

logger = get_logger(__name__)
EMBEDDING_DIM = 768  # text-embedding-004 output dimension


async def get_embeddings(texts: list[str]) -> np.ndarray:
    """
    Embed texts using Google text-embedding-004, batched ≤100 per call.
    Returns float32 array of shape (len(texts), 768), L2-normalised.
    Falls back to random unit vectors when GEMINI_API_KEY is unset (dev/test).
    """
    if not texts:
        return np.zeros((0, EMBEDDING_DIM), dtype=np.float32)

    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set — using random unit vectors for embeddings")
        return _random_unit_vectors(len(texts))

    try:
        from google import genai  # type: ignore[import-untyped]

        client = genai.Client(api_key=api_key)
        all_values: list[list[float]] = []
        batch_size = 100

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            response = await client.aio.models.embed_content(
                model="text-embedding-004",
                contents=batch,
            )
            for emb in response.embeddings:
                all_values.append(emb.values)

        arr = np.array(all_values, dtype=np.float32)
    except Exception as exc:
        logger.error("Embedding API error: %s — falling back to random vectors", exc)
        return _random_unit_vectors(len(texts))

    return _l2_normalize(arr)


def _random_unit_vectors(n: int) -> np.ndarray:
    vecs = np.random.default_rng(seed=42).standard_normal((n, EMBEDDING_DIM)).astype(np.float32)
    return _l2_normalize(vecs)


def _l2_normalize(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    return arr / np.maximum(norms, 1e-9)
