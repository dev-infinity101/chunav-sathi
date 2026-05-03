"""
Builds the FAISS index from YAML knowledge base files.
Runs at Docker build time: python -m app.rag.index_builder

Full embedding + chunking logic implemented in Prompt 3.
This stub creates a valid empty index so Docker build succeeds.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import faiss
import numpy as np

DATA_DIR = Path(__file__).parent.parent.parent / "data"
INDEX_DIR = Path(__file__).parent.parent.parent / "faiss_index"
EMBEDDING_DIM = 768  # text-embedding-004 output dimension


def _create_placeholder_index() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    placeholder = np.zeros((1, EMBEDDING_DIM), dtype=np.float32)
    faiss.normalize_L2(placeholder)
    index.add(placeholder)
    faiss.write_index(index, str(INDEX_DIR / "index.faiss"))
    with open(INDEX_DIR / "meta.json", "w", encoding="utf-8") as f:
        json.dump([], f)
    print("Placeholder FAISS index written.", file=sys.stderr)


def build() -> None:
    yaml_files = list(DATA_DIR.glob("*.yaml"))
    if not yaml_files:
        print(
            f"No YAML files found in {DATA_DIR} — creating placeholder index.",
            file=sys.stderr,
        )
        _create_placeholder_index()
        return

    # Full chunking + embedding pipeline implemented in Prompt 3
    print(
        f"Found {len(yaml_files)} YAML files. Full build implemented in Prompt 3.",
        file=sys.stderr,
    )
    _create_placeholder_index()


if __name__ == "__main__":
    build()
