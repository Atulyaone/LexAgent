import io

import pytest
from pypdf import PdfWriter

from app.services.pdf_extractor import PDFExtractionError, extract_text_from_pdf


def _make_pdf_with_text(text: str) -> bytes:
    writer = PdfWriter()
    writer.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    writer.write(buffer)
    return buffer.getvalue()


def test_extract_text_rejects_empty_pdf(tmp_path):
    pdf_path = tmp_path / "empty.pdf"
    pdf_path.write_bytes(_make_pdf_with_text(""))

    with pytest.raises(PDFExtractionError, match="No extractable text"):
        extract_text_from_pdf(pdf_path)
