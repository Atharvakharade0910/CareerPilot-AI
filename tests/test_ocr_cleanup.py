"""OCR resource checks using a synthetic PDF and mocked Tesseract."""

import io

import fitz
import pytest
import pytesseract
from pypdf import PdfWriter

from app.services.resume_parser import document_text


@pytest.mark.parametrize("ocr_fails", [False, True])
def test_scanned_pdf_is_closed_after_ocr(monkeypatch, ocr_fails):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = io.BytesIO()
    writer.write(buffer)
    data = buffer.getvalue()
    document = fitz.open(stream=data, filetype="pdf")
    monkeypatch.setattr(fitz, "open", lambda **kwargs: document)
    expected = "Skills: Python and FastAPI. Built a study assistant."

    def recognize(*args, **kwargs):
        if ocr_fails:
            raise RuntimeError("Synthetic OCR failure")
        return expected

    monkeypatch.setattr(pytesseract, "image_to_string", recognize)
    try:
        if ocr_fails:
            with pytest.raises(ValueError, match="needs local OCR"):
                document_text(data, "scanned.pdf")
        else:
            assert document_text(data, "scanned.pdf") == expected
        assert document.is_closed
    finally:
        if not document.is_closed:
            document.close()
