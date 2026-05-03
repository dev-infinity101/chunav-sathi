from __future__ import annotations

from pathlib import Path

import yaml
from fastapi import APIRouter, HTTPException, Query

from app.core.logging import get_logger
from app.models.schemas import PhaseSchema, TimelineResponse

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["timeline"])

DATA_DIR = Path(__file__).parent.parent.parent / "data"
_VALID_LEVELS = {"lok_sabha", "vidhan_sabha", "panchayat"}

# Module-level cache — YAML is loaded once per level per process
_cache: dict[str, dict] = {}  # type: ignore[type-arg]


def _load_yaml(level: str) -> dict:  # type: ignore[type-arg]
    if level not in _cache:
        path = DATA_DIR / f"{level}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"No data file for level '{level}'")
        with open(path, encoding="utf-8") as f:
            _cache[level] = yaml.safe_load(f) or {}
        logger.info("Loaded YAML for level '%s'", level)
    return _cache[level]


@router.get("/timeline/{level}", response_model=TimelineResponse)
async def get_timeline(
    level: str,
    lang: str = Query(default="en", pattern="^(en|hi)$"),
) -> TimelineResponse:
    if level not in _VALID_LEVELS:
        raise HTTPException(status_code=404, detail=f"Unknown election level: '{level}'")

    try:
        data = _load_yaml(level)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    phases: list[PhaseSchema] = []
    for phase in data.get("phases", []):
        phases.append(
            PhaseSchema(
                id=phase.get("id", ""),
                order=phase.get("order", 0),
                name=phase.get(f"name_{lang}") or phase.get("name_en", ""),
                duration_days_typical=phase.get("duration_days_typical"),
                description=phase.get(f"description_{lang}") or phase.get("description_en", ""),
                key_facts=[str(f) for f in phase.get("key_facts", [])],
            )
        )

    return TimelineResponse(
        level=level,
        name=data.get(f"name_{lang}") or data.get("name_en", level),
        description=data.get(f"description_{lang}") or data.get("description_en", ""),
        phases=phases,
    )
