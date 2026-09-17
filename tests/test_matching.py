import pytest

from app.services.matching import score_job


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
