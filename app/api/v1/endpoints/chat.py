import json

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.services.llm_service import (
    get_chat_reply,
    stream_chat_reply,
    get_structured_chat_reply,
    ROLE_SYSTEM_PROMPTS,
)
from app.schemas.chat import ChatRequest, ChatResponse


router = APIRouter()

VALID_ROLES = list(ROLE_SYSTEM_PROMPTS.keys())


@router.post("/chat", response_model=ChatResponse)
async def chat(body: ChatRequest):
    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{body.role}'. Must be one of: {VALID_ROLES}",
        )

    reply = await get_chat_reply(body.role, [msg.model_dump() for msg in body.messages])
    return ChatResponse(reply=reply)


@router.post("/chat/stream")
async def chat_stream(body: ChatRequest):
    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{body.role}'. Must be one of: {VALID_ROLES}",
        )

    async def event_generator():
        async for token in stream_chat_reply(body.role, [msg.model_dump() for msg in body.messages]):
            yield f"data: {json.dumps({'text': token})}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@router.post("/chat/structured")
async def chat_structured(body: ChatRequest):
    """
    Experimental: returns structured JSON with description + points,
    or a simple chat reply, streamed via Server-Sent Events.
    """
    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{body.role}'. Must be one of: {VALID_ROLES}",
        )

    async def event_generator():
        result = await get_structured_chat_reply(
            body.role, [msg.model_dump() for msg in body.messages]
        )

        if result.get("type") == "chat":
            # Casual message: emit a single message event.
            yield (
                f"event: message\n"
                f"data: {json.dumps({'text': result.get('text', '')})}\n\n"
            )
        else:
            # Informational: emit description then numbered points.
            yield (
                f"event: description\n"
                f"data: {json.dumps({'text': result.get('description', '')})}\n\n"
            )
            for index, point in enumerate(result.get("points", []), start=1):
                yield (
                    f"event: point\n"
                    f"data: {json.dumps({'index': index, 'text': point})}\n\n"
                )

        yield "event: done\ndata: {}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )
