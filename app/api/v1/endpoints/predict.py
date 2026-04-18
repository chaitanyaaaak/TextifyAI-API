from fastapi import APIRouter, HTTPException

from app.services.llm_service import get_predictions, ROLE_SYSTEM_PROMPTS
from app.schemas.predict import PredictRequest, PredictResponse


router = APIRouter()

VALID_ROLES = list(ROLE_SYSTEM_PROMPTS.keys())


@router.post("/predict", response_model=PredictResponse)
async def predict(body: PredictRequest):
    if body.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role '{body.role}'. Must be one of: {VALID_ROLES}",
        )

    # Require at least 4 words before generating predictions.
    word_count = len(body.text.strip().split())
    if word_count < 4:
        return PredictResponse(predictions=[])

    predictions = await get_predictions(body.text, body.role, body.count)
    return PredictResponse(predictions=predictions)
