"""Exercise draft validation without a database or external provider."""
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api import intelligence


@pytest.mark.parametrize("values,expected", [
    (["Python"], True),
    (["Docker"], False),
    (["Python", "Docker"], False),
    ([], False),
])
def test_tailored_draft_pass_requires_nonempty_valid_claims(monkeypatch, values, expected):
    user = SimpleNamespace(id=uuid4())
    resume = SimpleNamespace(id=uuid4(), text="Built Python APIs.")
    job = SimpleNamespace(id=uuid4(), title="Developer", company="Example")
    evidence = [
        SimpleNamespace(id=uuid4(), value=value, evidence=resume.text)
        for value in values
    ]
    monkeypatch.setattr(intelligence, "latest", lambda db, u: resume)
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: evidence)
    saved = []
    db = SimpleNamespace(get=lambda model, key: job, add=saved.append, commit=lambda: None)

    result = intelligence.tailor(job.id, db=db, user=user)

    assert result["validation"]["passed"] is expected
    assert [claim["valid"] for claim in result["validation"]["claims"]] == [
        value == "Python" for value in values
    ]
    assert saved[0].validation == result["validation"]
    assert result["status"] == "draft"


@pytest.mark.parametrize("has_previous_approval", [False, True])
def test_approval_records_resume_version_used_for_hash(monkeypatch, has_previous_approval):
    import hashlib
    from datetime import datetime, timezone

    user = SimpleNamespace(id=uuid4())
    resume = SimpleNamespace(id=uuid4())
    application = SimpleNamespace(id=uuid4(), answers={"motivation": "Example"}, status="draft")
    old_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
    previous = SimpleNamespace(
        resume_id=uuid4(), approved=False, approved_at=old_time, content_hash="old"
    ) if has_previous_approval else None
    responses = iter([application, previous])
    saved = []
    commits = []
    db = SimpleNamespace(
        scalar=lambda query: next(responses), add=saved.append,
        commit=lambda: commits.append(True),
    )
    monkeypatch.setattr(intelligence, "latest", lambda db, u: resume)

    result = intelligence.approve(application.id, db=db, user=user)

    approval = previous if has_previous_approval else saved[0]
    digest = hashlib.sha256(f"{application.id}:{resume.id}:{application.answers}".encode()).hexdigest()
    assert approval.resume_id == resume.id
    assert approval.content_hash == result["approval_hash"] == digest
    assert approval.approved is True
    assert approval.approved_at > old_time
    assert application.status == result["status"] == "approved"
    assert len(saved) == (0 if has_previous_approval else 1)
    assert commits == [True]
