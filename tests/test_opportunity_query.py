"""Exercise local job-search query limits at the HTTP boundary."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api import opportunities


@pytest.mark.parametrize("query,expected_status", [
    ("Python", 200),
    ("x" * 120, 200),
    ("x" * 121, 422),
])
def test_local_job_search_query_limit(monkeypatch, query, expected_status):
    calls = []
    seeding = []
    database = SimpleNamespace(scalar=lambda statement: True, scalars=lambda statement: [])

    def get_database():
        calls.append(True)
        return database

    app = FastAPI()
    app.include_router(opportunities.router)
    app.dependency_overrides[opportunities.get_db] = get_database
    app.dependency_overrides[opportunities.current_user] = lambda: object()
    original_ensure_jobs = opportunities.ensure_jobs

    def track_seeding(db):
        seeding.append(True)
        return original_ensure_jobs(db)

    monkeypatch.setattr(opportunities, "ensure_jobs", track_seeding)

    with TestClient(app) as client:
        response = client.get("/api/jobs", params={"q": query})

    assert response.status_code == expected_status
    assert len(calls) == 1
    if expected_status == 422:
        assert seeding == []
    else:
        assert response.json() == []
        assert seeding == [True]


@pytest.mark.parametrize("query,location", [
    ("Python", "Pune"),
    ("  Python  ", "  Pune  "),
])
def test_live_job_search_trims_filter_whitespace(monkeypatch, query, location):
    rows = [{
        "external_id": "sample-role", "title": "Python Engineer", "company": "Example",
        "location": "Pune, India", "work_type": "any", "url": "https://arbeitnow.com/jobs/sample",
    }]
    monkeypatch.setattr(opportunities, "fetch_page", AsyncMock(return_value=(rows, "now", False, False)))
    monkeypatch.setattr(opportunities, "insert", lambda model: SimpleNamespace(
        values=lambda **kwargs: SimpleNamespace(
            excluded=SimpleNamespace(**kwargs),
            on_conflict_do_update=lambda **options: object(),
        )
    ))
    stored = SimpleNamespace(
        id="sample-id", company="Example", title="Python Engineer", location="Pune, India",
        work_type="any", experience_level="unspecified", salary="", source="arbeitnow",
        requirements={}, description="", posted_at="now", url="https://arbeitnow.com/jobs/sample",
    )
    db = SimpleNamespace(
        execute=lambda stmt: None, commit=lambda: None,
        scalars=lambda stmt: SimpleNamespace(all=lambda: [stored]),
    )
    app = FastAPI()
    app.include_router(opportunities.router)
    app.dependency_overrides[opportunities.get_db] = lambda: db

    with TestClient(app) as client:
        response = client.get("/api/jobs/search/live", params={"q": query, "location": location})

    assert response.status_code == 200
    assert len(response.json()["results"]) == 1
    assert response.json()["results"][0]["title"] == "Python Engineer"
    opportunities.fetch_page.assert_awaited_once_with(1)
