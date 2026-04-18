from pydantic import BaseModel


class UploadResponse(BaseModel):
    jobId: str
    status: str
    fileName: str


class StatusResponse(BaseModel):
    jobId: str
    status: str
    step: int
    totalSteps: int
    stepLabel: str


class CorrectionItem(BaseModel):
    original: str
    corrected: str
    line: int


class ReportResponse(BaseModel):
    jobId: str
    fileName: str
    totalWords: int
    totalErrors: int
    corrections: list[CorrectionItem]
