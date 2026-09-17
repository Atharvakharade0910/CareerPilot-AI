import pytest

from app.services.matching import aggregate_gaps, score_job


JOB = {
    "title": "Python Developer",
    "requirements": {"required": ["Python"], "preferred": []},
    "work_type": "remote",
}


@pytest.mark.parametrize("category", ["skills", "projects", "education", "experience"])
def test_rejected_fact_cannot_change_match(category):
    rejected = {"value": "Python", "category": category, "accepted": False}
    assert score_job({}, [rejected], JOB) == score_job({}, [], JOB)


@pytest.mark.parametrize("category", ["projects", "education", "experience"])
def test_accepted_evidence_still_contributes(category):
    fact = {"value": "Python", "category": category, "accepted": True}
    baseline = score_job({}, [], JOB)
    result = score_job({}, [fact], JOB)
    assert result["breakdown"][category] > baseline["breakdown"][category]
    assert result["score"] > baseline["score"]


def test_rejected_evidence_does_not_change_accepted_evidence_score():
    accepted = {"value": "Python", "category": "skills", "accepted": True}
    rejected = [
        {"value": "Python", "category": category, "accepted": False}
        for category in ["projects", "education", "experience"]
    ]
    assert score_job({}, [accepted, *rejected], JOB) == score_job({}, [accepted], JOB)


def test_unspecified_acceptance_keeps_existing_default():
    fact = {"value": "Python", "category": "projects"}
    assert score_job({}, [fact], JOB) == score_job({}, [{**fact, "accepted": True}], JOB)


def test_gap_frequency_counts_jobs_not_repeated_requirements():
    rows = [{"missing": ["Python", "python", " Python "]}] * 5
    assert aggregate_gaps(rows) == [{
        "skill": "python", "occurrences": 5, "jobs_analyzed": 5,
        "frequency": 100, "priority": "critical",
    }]


def test_gap_aliases_count_once_per_job_and_keep_correct_priority():
    rows = [
        {"missing": ["Postgres", "PostgreSQL"]},
        {"missing": ["postgresql"]},
        {"missing": ["postgres"]},
        {"missing": []},
        {},
    ]
    assert aggregate_gaps(rows) == [{
        "skill": "postgresql", "occurrences": 3, "jobs_analyzed": 5,
        "frequency": 60, "priority": "high",
    }]


def test_gap_report_ignores_blank_skills():
    assert aggregate_gaps([{"missing": ["", "  "]}] * 5) == []


def test_gap_report_still_requires_minimum_job_sample():
    assert aggregate_gaps([{"missing": ["Python"]}] * 4) == []
