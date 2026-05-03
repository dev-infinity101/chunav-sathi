from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from app.core.logging import get_logger
from app.core.security import limiter
from app.models.schemas import ChatRequest
from app.rag.retriever import retriever
from app.services.firestore import get_session_history, save_exchange
from app.services.gemini import stream_chat

logger = get_logger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])


def _detect_lang(text: str) -> str:
    """Return 'hi' if Devanagari characters are found, else 'en'."""
    for char in text:
        if "ऀ" <= char <= "ॿ":
            return "hi"
    return "en"


def _build_context_block(chunks: list) -> str:  # type: ignore[type-arg]
    if not chunks:
        return ""
    lines = ["Relevant context from knowledge base:"]
    for chunk in chunks:
        lines.append(f"[{chunk.source_id}] {chunk.text}")
    return "\n".join(lines)


def _sse(event: str, data: str) -> str:
    safe = json.dumps(data) if not data.startswith("{") else data
    return f"event: {event}\ndata: {safe}\n\n"


@router.post("/chat")
@limiter.limit("30/minute")
async def chat_endpoint(request: Request, body: ChatRequest) -> StreamingResponse:
    session_id = str(body.session_id)

    # Language: honour explicit lang but override if Devanagari detected
    lang = body.lang
    if _detect_lang(body.message) == "hi":
        lang = "hi"

    logger.info(
        "Chat request: session=%s lang=%s level=%s msg_len=%d",
        session_id,
        lang,
        body.level,
        len(body.message),
    )

    # Retrieve context + session history concurrently
    chunks, history = await asyncio.gather(
        retriever.retrieve(body.message, k=5, level=body.level, lang=lang),
        get_session_history(session_id, limit=10),
    )

    context_block = _build_context_block(chunks)
    prompt = f"{context_block}\n\nUser question: {body.message}" if context_block else body.message
    citations = [c.source_id for c in chunks]

    async def generate() -> None:
        full_response: list[str] = []

        try:
            async for token in stream_chat(prompt, history, lang):
                full_response.append(token)
                yield _sse("token", token)
        except Exception as exc:
            logger.error("Stream error: %s", exc)
            yield _sse("error", str(exc))

        yield f"event: done\ndata: {json.dumps({'citations': citations})}\n\n"

        # Persist after stream — fire-and-forget
        asyncio.create_task(
            save_exchange(
                session_id=session_id,
                user_msg=body.message,
                assistant_msg="".join(full_response),
                lang=lang,
                level=body.level,
                citations=citations,
            )
        )

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )
