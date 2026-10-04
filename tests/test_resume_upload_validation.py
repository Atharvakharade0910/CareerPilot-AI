"""Exercise resume upload metadata limits without persisting files."""

from io import BytesIO
from types import SimpleNamespace

import pytest
from fastapi import HTTPException

from app.api.routes import upload


@pytest.mark.parametrize("filename,expected_status", [
    ("resume.pdf", None),
    ("a" * 250 + ".pdf", None),
    ("a" * 251 + ".pdf", None),
    ("a" * 252 + ".pdf", 422),
])
def test_resume_filename_length_is_rejected_before_parsing(monkeypatch, filename, expected_status):
    file = SimpleNamespace(filename=filename, file=BytesIO(b"not parsed in this test"))
    db = SimpleNamespace()
    user = SimpleNamespace(id="test-user")

    if expected_status:
        monkeypatch.setattr("app.api.routes.document_text", lambda data, name: pytest.fail("should not parse overlong filename"))
        with pytest.raises(HTTPException) as error:
            upload(file=file, db=db, user=user)
        assert error.value.status_code == expected_status
        assert error.value.detail == "Resume filenames must be 255 characters or fewer."
    else:
        def reject_document(data, name):
            assert name == filename
            raise ValueError("Synthetic document validation")

        monkeypatch.setattr("app.api.routes.document_text", reject_document)
        with pytest.raises(HTTPException) as error:
            upload(file=file, db=db, user=user)
        assert error.value.status_code == 422
        assert error.value.detail == "Synthetic document validation"
