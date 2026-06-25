from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


class PDFExtractionError(Exception):
    """Raised when a PDF cannot be processed."""


@dataclass
class PDFExtractionResult:
    text: str
    page_count: int


def extract_text_from_pdf(file_path: Path) -> PDFExtractionResult:
    if not file_path.exists():
        raise PDFExtractionError(f"File not found: {file_path}")

    try:
        reader = PdfReader(str(file_path))
    except Exception as exc:
        raise PDFExtractionError(f"Unable to read PDF: {exc}") from exc

    if reader.is_encrypted:
        try:
            reader.decrypt("")
        except Exception as exc:
            raise PDFExtractionError(
                "PDF is encrypted and cannot be decrypted without a password"
            ) from exc

    page_count = len(reader.pages)
    if page_count == 0:
        raise PDFExtractionError("PDF contains no pages")

    pages_text: list[str] = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        pages_text.append(page_text.strip())

    text = "\n\n".join(part for part in pages_text if part).strip()
    if not text:
        raise PDFExtractionError(
            "No extractable text found. Upload a text-searchable PDF (OCR is not supported)."
        )

    return PDFExtractionResult(text=text, page_count=page_count)
