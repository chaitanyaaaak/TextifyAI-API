import json

from fastapi import APIRouter, HTTPException

from app.services.llm_service import (
    _get_client, 
    ROLE_SYSTEM_PROMPTS, 
    safe_extract_content, 
    safe_json_loads,
    logger
)
from app.core.config import settings
from app.schemas.coherence import CoherenceRequest, CoherenceResponse


router = APIRouter()

VALID_ROLES = list(ROLE_SYSTEM_PROMPTS.keys())
COHERENCE_LEVELS = ("low", "medium", "high")


@router.post("/coherence", response_model=CoherenceResponse)
async def detect_coherence(body: CoherenceRequest):
    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{body.role}'. Must be one of: {VALID_ROLES}",
        )

    if not body.sentence_a.strip() or not body.sentence_b.strip():
        raise HTTPException(
            status_code=400,
            detail="Both sentence_a and sentence_b are required and cannot be empty.",
        )

    role_context = ROLE_SYSTEM_PROMPTS[body.role]

    prompt = (
        f"{role_context}\n\n"
        "You are a coherence analysis expert. Analyze how logically and contextually "
        "sentence B follows from sentence A.\n\n"
        f'Sentence A: "{body.sentence_a}"\n'
        f'Sentence B: "{body.sentence_b}"\n\n'
        "Respond ONLY with valid json in this exact format:\n"
        '{"coherence": "<low|medium|high>", "score": <0-100>, '
        '"reason": "<one concise sentence explaining the coherence level>", '
        '"suggestion": "<one concise sentence on how to improve B, or empty string if coherence is high>"}'
    )

    client = _get_client()
    try:
        response = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=200,
            response_format={"type": "json_object"},
        )
    except Exception as e:
        logger.error(f"LLM call failed in coherence detection: {e}")
        raise HTTPException(
            status_code=502, 
            detail="Failed to communicate with AI service. Please try again later."
        )

    raw = safe_extract_content(response)
    result = safe_json_loads(raw)
    
    if not result or not isinstance(result, dict):
        logger.warning(f"Failed to parse coherence JSON. Raw response: {raw}")
        # Graceful fallback instead of 500
        return CoherenceResponse(
            coherence="medium",
            score=50,
            reason="AI response format was invalid, but sentences appear related.",
            suggestion="Try rephrasing for a clearer analysis."
        )

    try:
        coherence = str(result.get("coherence", "medium")).lower()
        if coherence not in COHERENCE_LEVELS:
            coherence = "medium"

        return CoherenceResponse(
            coherence=coherence,
            score=int(result.get("score", 50)),
            reason=result.get("reason", "Analysis complete."),
            suggestion=result.get("suggestion", ""),
        )
    except Exception as e:
        logger.error(f"Error processing coherence result: {e}. Result: {result}")
        raise HTTPException(status_code=500, detail="Error processing coherence analysis results.")
