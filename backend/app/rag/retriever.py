from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss  # type: ignore[import-untyped]
import numpy as np

from app.core.logging import get_logger
from app.rag.embed import EMBEDDING_DIM, get_embeddings

logger = get_logger(__name__)
INDEX_DIR = Path(__file__).parent.parent.parent / "faiss_index"


@dataclass
class Chunk:
    text: str
    level: str
    type: str
    lang: str
    score: float
    source_id: str


class Retriever:
    def __init__(self, index_dir: Path = INDEX_DIR) -> None:
        index_path = index_dir / "index.faiss"
        meta_path = index_dir / "meta.json"
        if index_path.exists() and meta_path.exists():
            self._index: faiss.Index = faiss.read_index(str(index_path))
            with open(meta_path, encoding="utf-8") as f:
                self._meta: list[dict] = json.load(f)  # type: ignore[type-arg]
            logger.info(
                "Retriever loaded %d vectors from %s", self._index.ntotal, index_dir
            )
        else:
            logger.warning("FAISS index not found at %s — retriever disabled", index_dir)
            self._index = None  # type: ignore[assignment]
            self._meta = []

    @property
    def is_ready(self) -> bool:
        return self._index is not None and len(self._meta) > 0

    async def retrieve(
        self,
        query: str,
        k: int = 5,
        level: str | None = None,
        lang: str = "en",
    ) -> list[Chunk]:
        if not self.is_ready:
            logger.warning("Retriever not ready — returning empty results")
            return []

        # Embed query
        q_vec = await get_embeddings([query])  # (1, 768) normalised

        # Pull top-20 candidates from FAISS
        n_probe = min(20, self._index.ntotal)
        scores, indices = self._index.search(q_vec, n_probe)  # type: ignore[arg-type]

        results: list[Chunk] = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0 or idx >= len(self._meta):
                continue
            meta = self._meta[idx]
            # Filter by lang and optionally by level
            if meta.get("lang") != lang:
                continue
            if level is not None and meta.get("level") != level:
                continue
            results.append(
                Chunk(
                    text=meta.get("text", ""),
                    level=meta.get("level", ""),
                    type=meta.get("type", ""),
                    lang=meta.get("lang", lang),
                    score=float(score),
                    source_id=meta.get("source_id", ""),
                )
            )
            if len(results) >= k:
                break

        return results


# Module-level singleton — loaded once at startup
retriever = Retriever()
