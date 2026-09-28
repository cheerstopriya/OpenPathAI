"""Bounded, source-linked investigation contracts."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

class InvestigationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    repository_url: str = Field(min_length=1, max_length=300)
    issue_number: int = Field(gt=0, le=2147483647, strict=True)

class InvestigationEvidence(BaseModel):
    id: str
    kind: str
    source_url: str
    text: str
    updated_at: datetime | None = None
    truncated: bool = False

class InvestigationStep(BaseModel):
    instruction: str
    evidence_ids: list[str]

class InvestigationResponse(BaseModel):
    repository_full_name: str
    issue_number: int
    issue_title: str
    issue_state: str
    fetched_at: datetime
    evidence: list[InvestigationEvidence]
    steps: list[InvestigationStep]
    warnings: list[str]
    generation_mode: str = "deterministic"
