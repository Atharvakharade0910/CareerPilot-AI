from collections import Counter
from dataclasses import dataclass
import re

ALIASES = {"postgres": "postgresql", "sklearn": "scikit-learn", "gen ai": "generative ai", "llm": "large language models"}
WEIGHTS = {"required_skills": 35, "preferred_skills": 10, "projects": 15, "role": 10, "education": 10, "experience": 10, "location": 5, "tools": 5}

def normalize(value: str) -> str:
    value = re.sub(r"\s+", " ", value.lower().strip())
    return ALIASES.get(value, value)


def contains_term(text: str, term: str) -> bool:
    return bool(term and re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", text))

def score_job(profile: dict, facts: list[dict], job: dict) -> dict:
    facts = [f for f in facts if f.get("accepted", True) and normalize(f["value"])]
    accepted = [normalize(f["value"]) for f in facts]
    accepted_set = set(accepted)
    req = list(dict.fromkeys(filter(None, (normalize(s) for s in job.get("requirements", {}).get("required", [])))))
    pref = list(dict.fromkeys(filter(None, (normalize(s) for s in job.get("requirements", {}).get("preferred", [])))))
    matched = [s for s in req if s in accepted_set]
    partial = [s for s in req if s not in matched and any(contains_term(a, s) or contains_term(s, a) for a in accepted)]
    missing = [s for s in req if s not in matched and s not in partial]
    def ratio(items, hits): return (len(hits) / len(items) * 100) if items else 100
    skill = ratio(req, matched)
    pref_score = ratio(pref, [s for s in pref if s in accepted_set])
    project_evidence = [normalize(f["value"]) for f in facts if f.get("category") in {"projects", "experience"}]
    project_score = 100 if any(contains_term(text, s) for text in project_evidence for s in req) else 45
    role_terms = set(normalize(job["title"]).split())
    roles = [set(normalize(r).split()) for r in profile.get("target_roles", [])]
    role_score = 100 if any(role_terms & r for r in roles) else 55
    location = profile.get("locations", [])
    location_score = 100 if not location or job.get("work_type") == "remote" or any(normalize(x) in normalize(job.get("location", "")) for x in location) else 35
    breakdown = {"required_skills": round(skill), "preferred_skills": round(pref_score), "projects": round(project_score), "role": round(role_score), "education": 70 if any(f.get("category") == "education" for f in facts) else 0, "experience": 75 if any(f.get("category") == "experience" for f in facts) else 35, "location": round(location_score), "tools": round(ratio(req, matched))}
    overall = round(sum(breakdown[k] * WEIGHTS[k] for k in WEIGHTS) / 100, 1)
    return {"score": overall, "breakdown": breakdown, "matched": matched, "partial": partial, "missing": missing, "explanation": f"Matched {len(matched)} of {len(req)} required skills. {len(missing)} requirements need stronger evidence."}

def aggregate_gaps(rows: list[dict], minimum_jobs: int = 5) -> list[dict]:
    if len(rows) < minimum_jobs: return []
    counts = Counter(
        skill
        for row in rows
        for skill in dict.fromkeys(normalize(s) for s in row.get("missing", []))
        if skill
    )
    return [{"skill": skill, "occurrences": count, "jobs_analyzed": len(rows), "frequency": round(count / len(rows) * 100), "priority": "critical" if count / len(rows) >= .7 else "high" if count / len(rows) >= .5 else "watch"} for skill, count in counts.most_common()]
