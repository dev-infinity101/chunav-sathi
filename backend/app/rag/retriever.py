from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import numpy as np

INDEX_DIR = Path(__file__).parent.parent.parent / "faiss_index"

# Full implementation: Prompt 3


@dataclass
class Chunk:
    text: str
    level: str
    type: str
    lang: str
    score: float
    source_id: str


class Retriever:
    def __init__(self) -> None:
        index_path = INDEX_DIR / "index.faiss"
        meta_path = INDEX_DIR / "meta.json"
        if index_path.exists() and meta_path.exists():
            self._index: faiss.Index = faiss.read_index(str(index_path))
            with open(meta_path, encoding="utf-8") as f:
                self._meta: list[dict] = json.load(f)  # type: ignore[type-arg]
        else:
            self._index = None  # type: ignore[assignment]
            self._meta = []

    def retrieve(
        self,
        query: str,
        k: int = 5,
        level: str | None = None,
        lang: str = "en",
    ) -> list[Chunk]:
        """Stub — returns empty list. Real FAISS retrieval in Prompt 3."""
        return []


# Module-level singleton loaded once at startup
retriever = Retriever()
