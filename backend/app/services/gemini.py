from typing import AsyncIterator

# Full implementation: Prompt 4


async def stream_chat(
    prompt: str,
    history: list[dict],  # type: ignore[type-arg]
    lang: str,
) -> AsyncIterator[str]:
    """Stub — yields nothing. Real streaming in Prompt 4."""
    return
    yield  # makes this an async generator
