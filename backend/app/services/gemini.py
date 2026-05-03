from __future__ import annotations

from typing import AsyncIterator

from app.core.logging import get_logger
from app.services.secrets import get_secret

logger = get_logger(__name__)

SYSTEM_PROMPT = (
    "You are Chunav Saathi, a helpful assistant for Indian voters. "
    "Always ground your answers in the provided context. "
    "If the user wrote in Hindi, respond in Hindi. If English, respond in English. "
    "Be concise (under 150 words). "
    "Cite source titles when possible. "
    "Never invent dates, statistics, or laws not present in the context. "
    "If you do not know, say so."
)

_MODEL = "gemini-2.5-flash"


async def stream_chat(
    prompt: str,
    history: list[dict],  # type: ignore[type-arg]
    lang: str,
) -> AsyncIterator[str]:
    """
    Stream Gemini tokens for a single user turn.

    Args:
        prompt:  Full user message, may include prepended context block.
        history: List of {"role": "user"|"model", "text": str} dicts (oldest first).
        lang:    "en" or "hi" — used only for logging.
    Yields:
        Text tokens as they arrive from Gemini.
    """
    api_key = get_secret("GEMINI_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY unavailable — stream_chat is a no-op")
        return

    try:
        from google import genai  # type: ignore[import-untyped]
        from google.genai import types  # type: ignore[import-untyped]

        client = genai.Client(api_key=api_key)

        contents = []
        for turn in history:
            contents.append(
                types.Content(
                    role=turn["role"],
                    parts=[types.Part(text=turn["text"])],
                )
            )
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=prompt)],
            )
        )

        async for chunk in await client.aio.models.generate_content_stream(
            model=_MODEL,
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                max_output_tokens=600,
            ),
        ):
            if chunk.text:
                yield chunk.text

    except Exception as exc:
        logger.error("Gemini streaming error (lang=%s): %s", lang, exc)
        yield f"[Error: Could not fetch response — {exc}]"
