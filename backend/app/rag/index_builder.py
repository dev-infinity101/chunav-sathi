"""
Builds the FAISS index from YAML knowledge base files.
Run at Docker build time: python -m app.rag.index_builder

Chunks every phase, tier, key_concept, FAQ, and glossary term into
separate EN and HI entries. Embeds them and stores an IndexFlatIP
(inner-product on L2-normalised vectors ≡ cosine similarity).
"""
from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

import faiss  # type: ignore[import-untyped]
import numpy as np
import yaml

from app.rag.embed import EMBEDDING_DIM, get_embeddings

DATA_DIR = Path(__file__).parent.parent.parent / "data"
INDEX_DIR = Path(__file__).parent.parent.parent / "faiss_index"


# ---------------------------------------------------------------------------
# Chunk extraction helpers
# ---------------------------------------------------------------------------

def _text_or(d: dict[str, Any], *keys: str, fallback: str = "") -> str:
    for k in keys:
        v = d.get(k)
        if v:
            return str(v)
    return fallback


def _extract_phases(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for phase in data.get("phases", []):
        for lang in ("en", "hi"):
            parts = [
                f"Phase: {_text_or(phase, f'name_{lang}')}",
                _text_or(phase, f"description_{lang}"),
            ]
            if phase.get("key_facts"):
                parts.append("Key facts: " + "; ".join(str(f) for f in phase["key_facts"]))
            chunks.append(
                {
                    "text": "\n".join(p for p in parts if p),
                    "level": level,
                    "type": "phase",
                    "lang": lang,
                    "title": _text_or(phase, f"name_{lang}", "id"),
                    "source_id": f"{level}:phase:{phase.get('id', '')}:{lang}",
                }
            )
    return chunks


def _extract_tiers(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for tier in data.get("tiers", []):
        for lang in ("en", "hi"):
            parts = [
                f"Tier: {_text_or(tier, f'name_{lang}')}",
                _text_or(tier, f"description_{lang}"),
            ]
            if tier.get("key_facts"):
                parts.append("Key facts: " + "; ".join(str(f) for f in tier["key_facts"]))
            chunks.append(
                {
                    "text": "\n".join(p for p in parts if p),
                    "level": level,
                    "type": "tier",
                    "lang": lang,
                    "title": _text_or(tier, f"name_{lang}", "id"),
                    "source_id": f"{level}:tier:{tier.get('id', '')}:{lang}",
                }
            )
    return chunks


def _extract_key_concepts(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for concept in data.get("key_concepts", []):
        for lang in ("en", "hi"):
            full = concept.get(f"full_form_{lang}") or concept.get("full_form", "")
            parts = [
                f"Concept: {concept.get('term', '')} ({full})",
                _text_or(concept, f"explanation_{lang}"),
            ]
            chunks.append(
                {
                    "text": "\n".join(p for p in parts if p),
                    "level": level,
                    "type": "key_concept",
                    "lang": lang,
                    "title": concept.get("term", ""),
                    "source_id": f"{level}:concept:{concept.get('term','').lower().replace(' ','_')}:{lang}",
                }
            )
    return chunks


def _extract_faqs(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for i, faq in enumerate(data.get("faqs", [])):
        for lang in ("en", "hi"):
            q = faq.get(f"q_{lang}", "")
            a = faq.get(f"a_{lang}", "")
            if q and a:
                chunks.append(
                    {
                        "text": f"Q: {q}\nA: {a}",
                        "level": level,
                        "type": "faq",
                        "lang": lang,
                        "title": q[:80],
                        "source_id": f"{level}:faq:{i}:{lang}",
                    }
                )
    return chunks


def _extract_glossary_terms(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for term_data in data.get("terms", []):
        for lang in ("en", "hi"):
            parts = [
                f"Term: {term_data.get('term', '')} ({_text_or(term_data, f'full_form_{lang}')})",
                _text_or(term_data, f"explanation_{lang}"),
            ]
            chunks.append(
                {
                    "text": "\n".join(p for p in parts if p),
                    "level": level,
                    "type": "glossary",
                    "lang": lang,
                    "title": term_data.get("term", ""),
                    "source_id": f"{level}:glossary:{term_data.get('term','').lower()}:{lang}",
                }
            )
    return chunks


def _extract_eligibility(data: dict[str, Any], level: str) -> list[dict[str, Any]]:
    chunks = []
    for house, house_data in data.get("candidate_eligibility", {}).items():
        if not isinstance(house_data, dict):
            continue
        for lang in ("en", "hi"):
            title_key = f"title_{lang}"
            title = house_data.get(title_key, house)
            parts = [title]
            for cond in house_data.get("conditions", []):
                cond_text = cond.get(f"condition_{lang}", "")
                if cond_text:
                    parts.append(f"- {cond_text}")
            chunks.append(
                {
                    "text": "\n".join(p for p in parts if p),
                    "level": level,
                    "type": "eligibility",
                    "lang": lang,
                    "title": title,
                    "source_id": f"{level}:eligibility:{house}:{lang}",
                }
            )

    ve = data.get("voter_eligibility", {})
    for lang in ("en", "hi"):
        parts = [ve.get(f"title_{lang}", "Voter Eligibility")]
        for cond in ve.get("conditions", []):
            cond_text = cond.get(f"condition_{lang}", "")
            note = cond.get(f"note_{lang}", "")
            if cond_text:
                entry = f"- {cond_text}"
                if note:
                    entry += f" {note}"
                parts.append(entry)
        chunks.append(
            {
                "text": "\n".join(p for p in parts if p),
                "level": level,
                "type": "eligibility",
                "lang": lang,
                "title": ve.get(f"title_{lang}", "Voter Eligibility"),
                "source_id": f"{level}:eligibility:voter:{lang}",
            }
        )
    return chunks


def _chunk_file(path: Path) -> list[dict[str, Any]]:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data:
        return []

    level = data.get("level", path.stem)
    chunks: list[dict[str, Any]] = []

    chunks.extend(_extract_phases(data, level))
    chunks.extend(_extract_tiers(data, level))
    chunks.extend(_extract_key_concepts(data, level))
    chunks.extend(_extract_faqs(data, level))
    chunks.extend(_extract_glossary_terms(data, level))

    if level == "eligibility":
        chunks.extend(_extract_eligibility(data, level))

    return chunks


# ---------------------------------------------------------------------------
# Build function
# ---------------------------------------------------------------------------

async def _build(data_dir: Path, index_dir: Path) -> None:
    yaml_files = sorted(data_dir.glob("*.yaml"))
    if not yaml_files:
        print(f"[index_builder] No YAML files in {data_dir}", file=sys.stderr)
        return

    all_chunks: list[dict[str, Any]] = []
    for path in yaml_files:
        file_chunks = _chunk_file(path)
        all_chunks.extend(file_chunks)
        print(f"[index_builder] {path.name}: {len(file_chunks)} chunks", file=sys.stderr)

    print(f"[index_builder] Total chunks: {len(all_chunks)}", file=sys.stderr)

    texts = [c["text"] for c in all_chunks]
    vectors = await get_embeddings(texts)  # (N, 768) float32, L2-normalised

    index = faiss.IndexFlatIP(EMBEDDING_DIM)
    index.add(vectors)  # type: ignore[arg-type]

    index_dir.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(index_dir / "index.faiss"))
    with open(index_dir / "meta.json", "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, ensure_ascii=False)

    print(
        f"[index_builder] Saved index ({index.ntotal} vectors) → {index_dir}",
        file=sys.stderr,
    )


def build(data_dir: Path = DATA_DIR, index_dir: Path = INDEX_DIR) -> None:
    asyncio.run(_build(data_dir, index_dir))


if __name__ == "__main__":
    build()
