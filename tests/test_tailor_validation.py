"""Exercise draft validation without a database or external provider."""
from types import SimpleNamespace
from uuid import uuid4

import pytest

from app.api import intelligence


@pytest.mark.parametrize("claim,evidence,expected", [
    ("Java", "Built JavaScript applications.", False),
    ("SQL", "Used PostgreSQL databases.", False),
    ("10", "Served 100 customers.", False),
    ("Java", "Built Java applications.", True),
    ("C++", "Built C++ applications.", True),
    ("SQL", "Built SQL-based reports.", True),
    ("Built Python APIs.", "Built Python APIs.", True),
])
def test_tailored_claim_requires_complete_text(monkeypatch, claim, evidence, expected):
    user = SimpleNamespace(id=uuid4())
    resume = SimpleNamespace(id=uuid4(), text=evidence)
    job = SimpleNamespace(id=uuid4(), title="Developer", company="Example")
    monkeypatch.setattr(intelligence, "latest", lambda db, u: resume)
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: [
        SimpleNamespace(id=uuid4(), value=claim, evidence=evidence),
    ])
    saved = []
    db = SimpleNamespace(get=lambda model, key: job, add=saved.append, commit=lambda: None)

    result = intelligence.tailor(job.id, db=db, user=user)

    assert result["validation"]["passed"] is expected
    assert result["validation"]["claims"][0]["valid"] is expected
    assert saved[0].validation == result["validation"]


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


@pytest.mark.parametrize("count", [3, 25])
@pytest.mark.parametrize("provider_fails", [False, True])
def test_assistant_references_only_supplied_evidence(monkeypatch, count, provider_fails):
    import asyncio
    from unittest.mock import AsyncMock

    evidence = [SimpleNamespace(id=uuid4(), value=f"Evidence item {i:02d}") for i in range(count)]
    monkeypatch.setattr(intelligence, "latest", lambda db, u: SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: evidence)
    generate = AsyncMock(return_value="Example response")
    if provider_fails:
        generate.side_effect = intelligence.GeminiUnavailable("Synthetic failure")
    monkeypatch.setattr(intelligence, "generate", generate)

    result = asyncio.run(intelligence.assistant("Summarize my profile", db=object(), user=object()))

    limit = 8 if provider_fails else 20
    assert result["evidence_ids"] == [str(f.id) for f in evidence[:limit]]
    assert result["provider"] == ("local" if provider_fails else "gemini")
    generate.assert_awaited_once()
    prompt = generate.call_args.args[0]
    for fact in evidence[:20]:
        assert fact.value in prompt
    for fact in evidence[20:]:
        assert fact.value not in prompt
    if provider_fails:
        for fact in evidence[:8]:
            assert fact.value in result["message"]
        for fact in evidence[8:]:
            assert fact.value not in result["message"]


@pytest.mark.parametrize("values", [[], [""], [" ", "\t\n"]])
@pytest.mark.parametrize("query", ["Summarize my profile", "What should I learn?"])
def test_assistant_needs_usable_accepted_evidence(monkeypatch, values, query):
    import asyncio
    from unittest.mock import AsyncMock

    monkeypatch.setattr(intelligence, "latest", lambda db, u: SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: [
        SimpleNamespace(id=uuid4(), value=value) for value in values
    ])
    generate = AsyncMock()
    monkeypatch.setattr(intelligence, "generate", generate)
    result = asyncio.run(intelligence.assistant(query, db=object(), user=object()))
    assert result["provider"] == "local"
    assert result["evidence_ids"] == []
    assert "accept at least one fact" in result["message"]
    generate.assert_not_awaited()


@pytest.mark.parametrize("query,expected_status", [
    ("", 422),
    (" \t\n", 422),
    ("\u2003\u00a0", 422),
    ("x" * 4001, 422),
    ("x" * 4000, 200),
    ("  Summarize my profile.\n", 200),
])
def test_assistant_question_validation_over_http(monkeypatch, query, expected_status):
    from unittest.mock import AsyncMock, Mock

    from fastapi import FastAPI
    from fastapi.testclient import TestClient

    app = FastAPI()
    app.include_router(intelligence.router)
    app.dependency_overrides[intelligence.get_db] = lambda: object()
    app.dependency_overrides[intelligence.current_user] = lambda: object()
    latest = Mock(return_value=SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(intelligence, "latest", latest)
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: [
        SimpleNamespace(id=uuid4(), value="Python"),
    ])
    generate = AsyncMock(return_value="Grounded response")
    monkeypatch.setattr(intelligence, "generate", generate)

    with TestClient(app) as client:
        response = client.post("/api/assistant", params={"query": query})

    assert response.status_code == expected_status
    if expected_status == 422:
        assert response.json()["detail"] == (
            "Keep your question to 4,000 characters or fewer." if query.strip()
            else "Enter a question for the career assistant."
        )
        latest.assert_not_called()
        generate.assert_not_awaited()
    else:
        assert response.json()["message"] == "Grounded response"
        latest.assert_called_once()
        generate.assert_awaited_once()
        assert f"\nUser question: {query.strip()}\nAnswer concisely" in generate.call_args.args[0]


@pytest.mark.parametrize("query", ["What should I learn?", "Explain my SKILL GAPS", "Suggest learning resources", "Create a learning plan"])
def test_generic_learning_reply_does_not_cite_resume_evidence(monkeypatch, query):
    import asyncio
    from unittest.mock import AsyncMock

    monkeypatch.setattr(intelligence, "latest", lambda db, u: SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: [
        SimpleNamespace(id=uuid4(), value="Python"),
        SimpleNamespace(id=uuid4(), value="Built APIs"),
    ])
    generate = AsyncMock()
    monkeypatch.setattr(intelligence, "generate", generate)

    result = asyncio.run(intelligence.assistant(query, db=object(), user=object()))

    assert result["provider"] == "local"
    assert "five relevant roles" in result["message"]
    assert result["evidence_ids"] == []
    generate.assert_not_awaited()


@pytest.mark.parametrize("query", [
    "Summarize my machine learning projects",
    "Describe my scikit-learn experience",
    "What have I learned from my projects?",
])
def test_profile_questions_about_learning_reach_generation(monkeypatch, query):
    import asyncio
    from unittest.mock import AsyncMock

    fact = SimpleNamespace(id=uuid4(), value="Built machine learning models with scikit-learn")
    monkeypatch.setattr(intelligence, "latest", lambda db, u: SimpleNamespace(id=uuid4()))
    monkeypatch.setattr(intelligence, "facts", lambda db, u, r: [fact])
    generate = AsyncMock(return_value="Evidence-grounded profile response")
    monkeypatch.setattr(intelligence, "generate", generate)

    result = asyncio.run(intelligence.assistant(query, db=object(), user=object()))

    assert result["provider"] == "gemini"
    assert result["evidence_ids"] == [str(fact.id)]
    assert result["message"] == "Evidence-grounded profile response"
    generate.assert_awaited_once()
    assert query in generate.call_args.args[0]
