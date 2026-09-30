from dataclasses import dataclass, field
from typing import Any


@dataclass
class RiskResult:
    score: float
    level: str
    factors: list[str] = field(default_factory=list)


@dataclass
class PolicyResult:
    policy_id: str
    action: str
    reason: str


@dataclass
class ApprovalResult:
    required: bool
    status: str


@dataclass
class DecisionResult:
    decision_id: str
    request: str

    source: str
    classification: str
    confidence: float | None

    risk: RiskResult
    policy: PolicyResult
    approval: ApprovalResult

    evidence: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)