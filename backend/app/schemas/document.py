from pydantic import BaseModel


class DocumentUploadResponse(BaseModel):
    doc_id: str
    filename: str
    page_count: int
    status: str
    text_preview: str
