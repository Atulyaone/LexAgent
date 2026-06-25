import io

from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.main import app


def _sample_pdf_bytes() -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_health_check():
    client = TestClient(app)
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "version": "milestone-1"}


def test_upload_rejects_non_pdf():
    client = TestClient(app)
    response = client.post(
        "/api/documents/upload",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400


def test_analyze_unknown_document_returns_404():
    client = TestClient(app)
    response = client.post(
        "/api/agents/analyze",
        json={"doc_id": "doc_missing"},
    )
    assert response.status_code == 404
