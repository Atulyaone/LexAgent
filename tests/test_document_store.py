from pathlib import Path

import pytest

from app.services.document_store import DocumentStore


def test_get_rehydrates_document_from_disk(tmp_path):
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()
    pdf_source = Path(__file__).resolve().parents[1] / "backend" / "uploads"
    existing = next(pdf_source.glob("doc_*_*.PDF"), None) or next(pdf_source.glob("doc_*_*.pdf"), None)
    if existing is None:
        pytest.skip("No uploaded PDF fixture available")

    doc_id = existing.name.split("_", 1)[0]
    target = upload_dir / existing.name
    target.write_bytes(existing.read_bytes())

    store = DocumentStore(upload_dir=upload_dir)
    document = store.get(doc_id)

    assert document.doc_id == doc_id
    assert document.page_count > 0
    assert document.raw_text
