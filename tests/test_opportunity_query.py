"""Exercise local job-search query limits at the HTTP boundary."""

from types import SimpleNamespace

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
