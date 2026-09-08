"""Phase 4 contract. No autonomous graph executes in Phase 1."""

from typing import TypedDict, NotRequired, Literal


class CareerAgentState(TypedDict):
    user_id: str
    user_query: str
    candidate_profile: dict
    selected_job: NotRequired[dict]
    evidence_ids: list[str]
    requires_approval: bool
    status: Literal["pending", "running", "awaiting_review", "failed", "complete"]
