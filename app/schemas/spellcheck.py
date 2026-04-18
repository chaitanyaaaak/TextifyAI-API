from pydantic import BaseModel


class SpellCheckRequest(BaseModel):
    text: str


class Correction(BaseModel):
    word: str
    correction: str
    offset: int
    length: int


class SpellCheckResponse(BaseModel):
    corrections: list[Correction]
    auto_corrected_text: str
