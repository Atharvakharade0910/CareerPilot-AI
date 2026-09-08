"""Run from backend: python -m pytest ../tests -q
Uses the configured PostgreSQL database; creates and removes only test-owned users.
"""

import io, uuid
import pytest
from docx import Document
from fastapi.testclient import TestClient
from sqlalchemy import delete, select
from app.main import app
from app.core.database import SessionLocal
from app.core.config import settings
from app.models.entities import User, ResumeVersion
from app.services.resume_parser import extract, document_text, validate_claim

TEXT = """Taylor Test
Skills
Python, FastAPI, Postgres, SKLearn, Gen AI
Education
Bachelor of Computer Science, 2025
Projects
Built a FastAPI study assistant using Python.
Certifications
Introduction to AI course, 2025
"""


def docx_bytes(text=TEXT):
    d = Document()
    for line in text.splitlines():
        d.add_paragraph(line)
    b = io.BytesIO()
    d.save(b)
    return b.getvalue()


@pytest.fixture
def accounts():
    clients = []
    ids = []
    for _ in range(2):
        c = TestClient(app)
        email = f"test-{uuid.uuid4()}@example.com"
        r = c.post(
            "/api/auth/register",
            json={
                "full_name": "Taylor Test",
                "email": email,
                "password": "Testing-only-9482!",
            },
        )
        assert r.status_code == 201, r.text
        ids.append(uuid.UUID(r.json()["id"]))
        clients.append(c)
    yield clients
    with SessionLocal() as db:
        for r in db.scalars(
            select(ResumeVersion).where(ResumeVersion.user_id.in_(ids))
        ):
            (settings.storage_dir / r.storage_key).unlink(missing_ok=True)
        db.execute(delete(User).where(User.id.in_(ids)))
        db.commit()
    for c in clients:
        c.close()


def test_extraction_is_grounded_and_normalized():
    parsed = extract(TEXT)
    values = {f.value for f in parsed.fields}
    assert {"PostgreSQL", "Scikit-learn", "Generative AI", "FastAPI"} <= values
    assert "AWS" not in values
    assert all(f.evidence in TEXT for f in parsed.fields)


def test_negated_skill_not_accepted():
    assert not extract("I have no experience with AWS.").fields


def test_truth_guard_rejects_fabricated_years():
    assert not validate_claim(
        "3 years of AWS experience",
        "Built a FastAPI study assistant using Python.",
        TEXT,
    )
    assert validate_claim(
        "FastAPI", "Built a FastAPI study assistant using Python.", TEXT
    )
    assert not validate_claim("Python", "Python", "Unrelated resume")


def test_docx_roundtrip():
    assert "FastAPI" in document_text(docx_bytes(), "resume.docx")


@pytest.mark.parametrize(
    "name,data",
    [("bad.pdf", b"fake"), ("bad.docx", b"invalid"), ("resume.exe", b"not a resume")],
)
def test_malformed_upload_rejected(accounts, name, data):
    assert (
        accounts[0].post("/api/resume/upload", files={"file": (name, data)}).status_code
        == 422
    )


def test_empty_resume_is_rejected():
    with pytest.raises(ValueError):
        document_text(docx_bytes(""), "empty.docx")


def test_full_profile_flow_and_isolation(accounts):
    a, b = accounts
    assert a.get("/api/profile").json()["resume"] is None
    original = docx_bytes()
    r = a.post("/api/resume/upload", files={"file": ("resume.docx", original)})
    assert r.status_code == 201, r.text
    rid = r.json()["id"]
    assert b.get("/api/resume/versions").json() == []
    assert b.get(f"/api/resume/{rid}/download").status_code == 404
    assert a.get(f"/api/resume/{rid}/download").content == original
    facts = a.get("/api/profile/facts").json()
    fact = facts[0]
    assert b.patch(f"/api/profile/facts/{fact['id']}?accepted=false").status_code == 404
    assert a.patch(f"/api/profile/facts/{fact['id']}?accepted=false").status_code == 200
    assert not next(f for f in a.get("/api/profile/facts").json() if f["id"] == fact["id"])["accepted"]
    payload = {
        "personal": {"full_name": "Taylor Test", "location": "Pune"},
        "preferences": {"target_roles": ["AI Engineer"]},
        "reviewed": True,
    }
    assert a.put("/api/profile", json=payload).status_code == 200
    assert a.get("/api/profile").json()["reviewed"]
    assert a.get("/api/analytics/overview").json()["profile_completeness"] == 100
    assert (
        a.post(
            "/api/resume/upload", files={"file": ("updated.docx", docx_bytes())}
        ).status_code
        == 201
    )
    assert not a.get("/api/profile").json()["reviewed"]
    assert len(a.get("/api/resume/versions").json()) == 2
    cookie = a.cookies.get("careerpilot_session")
    assert a.post("/api/auth/logout").status_code == 200
    assert a.get("/api/profile").status_code == 401
    a.cookies.set("careerpilot_session", cookie)
    assert a.get("/api/profile").status_code == 401


def test_authentication_and_csrf(accounts):
    a, _ = accounts
    assert a.get("/api/auth/me").status_code == 200
    assert (
        a.post(
            "/api/auth/logout", headers={"origin": "https://evil.example"}
        ).status_code
        == 403
    )
    assert a.get("/api/auth/me").status_code == 200
    assert TestClient(app).get("/api/profile").status_code == 401
    assert (
        a.post(
            "/api/auth/login",
            json={"email": "unknown@example.com", "password": "incorrect-password"},
        ).status_code
        == 401
    )
    assert a.post("/api/auth/forgot-password").status_code == 503


def test_cannot_complete_without_resume(accounts):
    assert (
        accounts[0]
        .put("/api/profile", json={"personal": {}, "preferences": {}, "reviewed": True})
        .status_code
        == 422
    )


def test_pdf_text_extraction():
    from pypdf import PdfWriter
    from pypdf.generic import DictionaryObject, NameObject, DecodedStreamObject

    writer = PdfWriter()
    page = writer.add_blank_page(width=612, height=792)
    font = DictionaryObject(
        {
            NameObject("/Type"): NameObject("/Font"),
            NameObject("/Subtype"): NameObject("/Type1"),
            NameObject("/BaseFont"): NameObject("/Helvetica"),
        }
    )
    page[NameObject("/Resources")] = DictionaryObject(
        {
            NameObject("/Font"): DictionaryObject(
                {NameObject("/F1"): writer._add_object(font)}
            )
        }
    )
    stream = DecodedStreamObject()
    stream.set_data(
        b"BT /F1 12 Tf 40 700 Td (Skills: Python and FastAPI. Built a study assistant.) Tj ET"
    )
    page[NameObject("/Contents")] = writer._add_object(stream)
    buf = io.BytesIO()
    writer.write(buf)
    assert "FastAPI" in document_text(buf.getvalue(), "resume.pdf")


def test_upload_size_limit(accounts):
    response = accounts[0].post(
        "/api/resume/upload",
        files={"file": ("large.pdf", b"x" * (5 * 1024 * 1024 + 1))},
    )
    assert response.status_code == 413
