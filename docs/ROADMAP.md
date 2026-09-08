# Implementation roadmap

| Phase | Deliverable | State |
|---|---|---|
| 1 | Professional shell, authentication, dashboard, onboarding, PostgreSQL and resume evidence | Implemented |
| 2 | Permitted job connectors, JD extraction, canonical skills, deterministic matching + embeddings | Local implementation |
| 3 | Recurring skill gaps, priority formulas, evidence-based learning plans and notifications | Gap aggregation implemented |
| 4 | Provider adapters, LangGraph orchestration, PostgreSQL checkpoints, grounded streaming assistant | Local bounded assistant; provider/graph pending |
| 5 | Evidence-constrained tailoring, Truth Guard, before/after diff, resume exports | Evidence-bound local draft; export/LLM pending |
| 6 | Application drafts, unknown-answer prompts, version-bound human approvals, tracker | Saved applications and approvals; full tracker pending |
| 7 | Allowlisted Playwright form adapters, progress capture and security-challenge pauses | Planned |
| 8 | Career analytics, market impact estimates, expanded evaluations and deployment hardening | Planned |

## Phase 2 scoring contract

Required skills 35; preferred skills 10; projects 15; role 10; education 10; experience 10; location 5; tools/domain 5. Store weights, component numerator/denominator, missing evidence and scoring version. Define missing-JD-field treatment before launch. The semantic component must be deterministic for a stored embedding/model version. Never expose a made-up LLM percentage.

The current implementation ships a local curated source in PostgreSQL and exposes `/api/jobs`, `/api/jobs/{id}/match`, `/api/skills/gaps`, and `/api/applications`. These fixtures remain explicitly local until a permitted external source is configured. Matching uses `weighted-v1` and is idempotent per user, job, and resume version.

The local API also exposes `/api/resume/tailor`, `/api/applications/{id}/approve`, `/api/assistant`, and notification read state. Tailoring is a conservative evidence-bound draft; assistant responses are explicitly local because no provider key is configured.

## Phase 3 evidence thresholds

At least five relevant analyzed jobs before alerts. Skills missing in 30/50/70% qualify as regular/high/critical alerts. Deduplicate reposts and use a fixed date window. Separate required vs preferred requirements and roles. Explain sample size and opportunity impact assumptions.

## Phase 4 graph

Intent router -> profile -> discovery -> JD analysis -> match -> gaps -> intelligence -> resume -> truth guard -> application -> human interrupt -> supported browser adapter -> tracking. Implement only intent-relevant branches, scope every tool to user_id, checkpoint failures, and test resumability. External documents cannot select tools or override policies.

## Phase 5/6 safety contract

Every generated claim references accepted evidence from an immutable resume version. An approval identifies exact resume and answer versions; changing either invalidates approval. Unknown salary, availability, notice periods and sensitive questions remain unanswered until the user provides them.

## Phase 7 browser contract

Start with a locally controlled test form. Allowlist supported forms and require explicit user approval to begin. Pause for CAPTCHA, authentication, security checks, ambiguous questions and unsupported forms. Never bypass protections. Do not equate successful field filling with successful application submission.
