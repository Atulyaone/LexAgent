from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.agents.orchestrator import orchestrator_agent
from app.config import settings
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse
from app.schemas.document import DocumentUploadResponse
from app.services.document_store import DocumentNotFoundError, document_store
from app.services.firac_generator import (
    FiracGenerationError,
    GeminiAPIError,
    GeminiConfigurationError,
)
from app.services.pdf_extractor import PDFExtractionError

app = FastAPI(
    title="LexAgent API",
    description="Milestone 1: PDF upload to FIRAC brief generation",
    version="milestone-1",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def ensure_upload_dir() -> None:
    settings.upload_path.mkdir(parents=True, exist_ok=True)


@app.get("/api/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "milestone-1"}


@app.post("/api/documents/upload", response_model=DocumentUploadResponse, status_code=201)
async def upload_document(file: UploadFile = File(...)) -> DocumentUploadResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > settings.max_upload_size_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"File exceeds maximum size of {settings.max_upload_size_mb}MB",
        )

    try:
        document = document_store.save_upload(file.filename, content)
    except PDFExtractionError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    if document.page_count > settings.max_pages:
        raise HTTPException(
            status_code=422,
            detail=(
                f"PDF has {document.page_count} pages, "
                f"which exceeds the Milestone 1 limit of {settings.max_pages} pages"
            ),
        )

    preview = document.raw_text[: settings.text_preview_length]
    if len(document.raw_text) > settings.text_preview_length:
        preview = f"{preview}..."

    return DocumentUploadResponse(
        doc_id=document.doc_id,
        filename=document.filename,
        page_count=document.page_count,
        status=document.status,
        text_preview=preview,
    )


@app.post(
    "/api/agents/analyze",
    response_model=AnalyzeResponse,
    tags=["agents"],
    summary="Analyze uploaded judgment and generate FIRAC brief",
    responses={
        404: {"description": "Uploaded document not found for the given doc_id"},
        422: {"description": "Invalid request or FIRAC generation failed"},
        502: {"description": "Gemini API upstream error"},
    },
)
async def analyze_document(request: AnalyzeRequest) -> AnalyzeResponse:
    try:
        return await orchestrator_agent.run_analysis(
            request.doc_id,
            model_name=settings.gemini_model,
        )
    except DocumentNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except GeminiConfigurationError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except GeminiAPIError as exc:
        err_msg = str(exc).lower()
        # Map quota limit, rate limit, or resource exhaustion to 503 Service Unavailable
        if "429" in err_msg or "quota" in err_msg or "rate limit" in err_msg or "exhausted" in err_msg:
            raise HTTPException(
                status_code=503,
                detail=f"Gemini API quota exhausted or service temporarily unavailable: {str(exc)}"
            ) from exc
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except FiracGenerationError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        err_msg = str(exc).lower()
        if "429" in err_msg or "quota" in err_msg or "rate limit" in err_msg or "exhausted" in err_msg:
            raise HTTPException(
                status_code=503,
                detail=f"Gemini API quota exhausted or service temporarily unavailable: {str(exc)}"
            ) from exc
        raise HTTPException(status_code=500, detail=str(exc)) from exc
