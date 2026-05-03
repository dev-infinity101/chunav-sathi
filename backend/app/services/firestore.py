# Full implementation: Prompt 4


async def save_exchange(
    session_id: str,
    user_msg: str,
    assistant_msg: str,
    lang: str,
    level: str | None,
    citations: list[str],
) -> None:
    """Stub — no-op. Real Firestore write in Prompt 4."""


async def get_session_history(session_id: str, limit: int = 10) -> list[dict]:  # type: ignore[type-arg]
    """Stub — returns empty history. Real Firestore read in Prompt 4."""
    return []
