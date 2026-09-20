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


@pytest.mark.parametrize("bucket", ["required", "preferred"])
def test_duplicate_requirements_do_not_change_match_score(bucket):
    facts = [{"value": "PostgreSQL", "category": "skills", "accepted": True}]
    clean_job = {**JOB, "requirements": {bucket: ["PostgreSQL", "Python"]}}
    duplicate_job = {**JOB, "requirements": {
        bucket: ["PostgreSQL", "Postgres", " POSTGRESQL ", "Python", "", "  "]
    }}
    assert score_job({}, facts, duplicate_job) == score_job({}, facts, clean_job)


def test_missing_requirements_are_unique_and_keep_original_order():
    job = {**JOB, "requirements": {
        "required": ["Python", "Postgres", "python", "PostgreSQL", "Docker"]
    }}
    result = score_job({}, [], job)
    assert result["missing"] == ["python", "postgresql", "docker"]
    assert result["explanation"] == "Matched 0 of 3 required skills. 3 requirements need stronger evidence."


def test_blank_requirements_behave_like_no_requirements():
    empty = {**JOB, "requirements": {"required": [], "preferred": []}}
    blank = {**JOB, "requirements": {"required": ["", " "], "preferred": ["\t"]}}
    assert score_job({}, [], blank) == score_job({}, [], empty)


@pytest.mark.parametrize("value", ["", "   ", "\t\n"])
@pytest.mark.parametrize("category", ["skills", "projects", "education", "experience"])
def test_blank_facts_do_not_change_match(value, category):
    blank = {"value": value, "category": category, "accepted": True}
    assert score_job({}, [blank], JOB) == score_job({}, [], JOB)


def test_blank_fact_does_not_hide_missing_skills_alongside_real_evidence():
    job = {**JOB, "requirements": {"required": ["Python", "Docker"]}}
    accepted = {"value": "Python", "category": "skills", "accepted": True}
    blank = {"value": "", "category": "experience", "accepted": True}
    result = score_job({}, [accepted, blank], job)
    assert result == score_job({}, [accepted], job)
    assert result["matched"] == ["python"]
    assert result["partial"] == []
    assert result["missing"] == ["docker"]
