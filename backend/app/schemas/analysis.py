from pydantic import BaseModel, Field

from app.schemas.firac import FiracBrief


class AnalyzeRequest(BaseModel):
    doc_id: str = Field(
        ...,
        min_length=1,
        description="Document ID returned by POST /api/documents/upload",
        examples=["doc_abc123def456"],
    )


class AnalysisMetadata(BaseModel):
    page_count: int
    model: str
    processing_time_ms: int


class AnalyzeResponse(BaseModel):
    doc_id: str
    filename: str
    status: str
    firac_brief: FiracBrief
    metadata: AnalysisMetadata
    error: str | None = None
