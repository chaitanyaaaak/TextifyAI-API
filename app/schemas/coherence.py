from pydantic import BaseModel


class CoherenceRequest(BaseModel):
    sentence_a: str
    sentence_b: str
    role: str = "student"


class CoherenceResponse(BaseModel):
    coherence: str   # "low" | "medium" | "high"
    score: int       # 0–100
    reason: str      # one-line explanation
    suggestion: str  # how to improve sentence_b (empty string if high)
