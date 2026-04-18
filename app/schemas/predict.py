from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    text: str
    role: str = "student"
    count: int = Field(default=5, ge=1, le=10)


class PredictResponse(BaseModel):
    predictions: list[str]
