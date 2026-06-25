import uuid
from dataclasses import dataclass
from pathlib import Path

from app.config import settings
from app.services.pdf_extractor import PDFExtractionResult, extract_text_from_pdf


class DocumentNotFoundError(Exception):
    """Raised when a document ID is unknown."""


@dataclass
class StoredDocument:
    doc_id: str
    filename: str
    file_path: Path
    page_count: int
    raw_text: str
    status: str


class DocumentStore:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.upload_path
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self._documents: dict[str, StoredDocument] = {}

    def save_upload(self, filename: str, content: bytes) -> StoredDocument:
        doc_id = f"doc_{uuid.uuid4().hex[:12]}"
        safe_name = Path(filename).name
        file_path = self.upload_dir / f"{doc_id}_{safe_name}"
        file_path.write_bytes(content)

        extraction = extract_text_from_pdf(file_path)
        document = StoredDocument(
            doc_id=doc_id,
            filename=safe_name,
            file_path=file_path,
            page_count=extraction.page_count,
            raw_text=extraction.text,
            status="UPLOADED",
        )
        self._documents[doc_id] = document
        return document

    def _load_from_disk(self, doc_id: str) -> StoredDocument | None:
        matches = sorted(self.upload_dir.glob(f"{doc_id}_*"))
        if not matches:
            return None

        file_path = matches[0]
        prefix = f"{doc_id}_"
        filename = file_path.name[len(prefix) :] if file_path.name.startswith(prefix) else file_path.name
        extraction = extract_text_from_pdf(file_path)
        return StoredDocument(
            doc_id=doc_id,
            filename=filename,
            file_path=file_path,
            page_count=extraction.page_count,
            raw_text=extraction.text,
            status="UPLOADED",
        )

    def get(self, doc_id: str) -> StoredDocument:
        document = self._documents.get(doc_id)
        if document is None:
            document = self._load_from_disk(doc_id)
            if document is not None:
                self._documents[doc_id] = document
        if document is None:
            raise DocumentNotFoundError(f"Document not found: {doc_id}")
        return document

    def mark_processed(self, doc_id: str) -> StoredDocument:
        document = self.get(doc_id)
        document.status = "PROCESSED"
        return document


document_store = DocumentStore()
