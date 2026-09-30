from dataclasses import dataclass, field
from typing import Optional


@dataclass
class SecurityDecision:
    decision_id: str
    request: str
    classification: str
    risk_score: float
    risk_level: str
    policy_action: str
    reason: str
    approval_required: bool
    evidence: list[str] = field(default_factory=list)
    classifier_source: Optional[str] = None


def create_decision(
    *,
    decision_id: str,
    request: str,
    classification: str,
    risk_score: float,
    risk_level: str,
    policy_action: str,
    reason: str,
    approval_required: bool,
    evidence: list[str] | None = None,
    classifier_source: str | None = None,
) -> SecurityDecision:

    return SecurityDecision(
        decision_id=decision_id,
        request=request,
        classification=classification,
        risk_score=risk_score,
        risk_level=risk_level,
        policy_action=policy_action,
        reason=reason,
        approval_required=approval_required,
        evidence=evidence or [],
        classifier_source=classifier_source,
    )