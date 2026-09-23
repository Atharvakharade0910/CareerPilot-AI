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
