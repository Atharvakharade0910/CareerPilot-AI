"""OCR resource checks using a synthetic PDF and mocked Tesseract."""

import io

import fitz
import pytest
import pytesseract
from pypdf import PdfWriter

from app.services.resume_parser import document_text


@pytest.mark.parametrize("failure", [None, "Synthetic OCR failure", "Tesseract process timeout"])
def test_scanned_pdf_is_closed_after_ocr(monkeypatch, failure):
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    buffer = io.BytesIO()
    writer.write(buffer)
    data = buffer.getvalue()
    document = fitz.open(stream=data, filetype="pdf")
    monkeypatch.setattr(fitz, "open", lambda **kwargs: document)
    expected = "Skills: Python and FastAPI. Built a study assistant."

    def recognize(*args, **kwargs):
        assert kwargs["timeout"] == 30
        if failure:
            raise RuntimeError(failure)
        return expected

    monkeypatch.setattr(pytesseract, "image_to_string", recognize)
    try:
        if failure:
            message = "30-second limit for a page" if failure == "Tesseract process timeout" else "needs local OCR"
            with pytest.raises(ValueError, match=message):
                document_text(data, "scanned.pdf")
        else:
            assert document_text(data, "scanned.pdf") == expected
        assert document.is_closed
    finally:
        if not document.is_closed:
            document.close()
