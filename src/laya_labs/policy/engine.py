from laya_labs.engine.schemas import (
    PolicyResult,
    RiskResult,
)
from laya_labs.policy.models import PolicyRule


class ConfiguredPolicyEngine:
    def __init__(self, rules: list[PolicyRule]):
        self.rules = sorted(rules, key=lambda rule: rule.priority)

    def evaluate(
        self,
        classification: str,
        environment: str,
        classification_source: str = "regex",
    ) -> PolicyResult:
        if classification == "READ_ONLY" and classification_source != "regex":
            return PolicyResult(
                policy_id="model-read-only-review",
                action="REQUIRES_REVIEW",
                reason="A model-classified read-only request requires deterministic review.",
            )
        for rule in self.rules:
            if rule.matches(classification, environment):
                return PolicyResult(
                    policy_id=rule.policy_id,
                    action=rule.action,
                    reason=rule.reason,
                )

        return PolicyResult(
            policy_id="unmatched-request",
            action="REQUIRES_REVIEW",
            reason="No configured policy matched; review is required.",
        )


def calculate_risk(
    classification: str,
    environment: str,
    privileged: bool = False,
    data_exposure: bool = False,
) -> RiskResult:

    score = 0.0
    factors = []

    if classification == "DESTRUCTIVE":
        score += 0.40
        factors.append("destructive_operation")

    if classification == "SECURITY_SENSITIVE":
        score += 0.25
        factors.append("security_sensitive")

    if classification == "MODIFY":
        score += 0.10
        factors.append("modify_operation")

    if environment == "production":
        score += 0.20
        factors.append("production_environment")

    if privileged:
        score += 0.10
        factors.append("privileged_operation")

    if data_exposure:
        score += 0.20
        factors.append("data_exposure")

    score = min(score, 1.0)

    if score >= 0.80:
        level = "CRITICAL"
    elif score >= 0.60:
        level = "HIGH"
    elif score >= 0.30:
        level = "MEDIUM"
    else:
        level = "LOW"

    return RiskResult(
        score=score,
        level=level,
        factors=factors,
    )


def evaluate_policy(
    classification: str,
    risk: RiskResult,
    environment: str,
    classification_source: str = "regex",
) -> PolicyResult:

    if risk.level == "CRITICAL":
        return PolicyResult(
            policy_id="critical-risk",
            action="BLOCK",
            reason="Critical-risk operation is blocked.",
        )

    if classification == "DESTRUCTIVE" and environment == "production":
        return PolicyResult(
            policy_id="production-destructive",
            action="REQUIRES_HUMAN_APPROVAL",
            reason="Destructive production operations require human approval.",
        )

    if classification == "DESTRUCTIVE":
        return PolicyResult(
            policy_id="destructive-operation",
            action="REQUIRES_REVIEW",
            reason="Destructive operations require review before execution.",
        )

    if classification == "PRIVILEGED":
        return PolicyResult(
            policy_id="privileged-operation",
            action="REQUIRES_HUMAN_APPROVAL",
            reason="Privileged operations require explicit human approval.",
        )

    if "privileged_operation" in risk.factors:
        return PolicyResult(
            policy_id="privileged-context",
            action="REQUIRES_HUMAN_APPROVAL",
            reason="Privileged context requires explicit human approval.",
        )

    if "data_exposure" in risk.factors:
        return PolicyResult(
            policy_id="data-exposure",
            action="REQUIRES_SECURITY_REVIEW",
            reason="Potential data exposure requires security review.",
        )

    if classification == "READ_ONLY" and classification_source != "regex":
        return PolicyResult(
            policy_id="model-read-only-review",
            action="REQUIRES_REVIEW",
            reason="A model-classified read-only request requires deterministic review.",
        )

    if classification == "SECURITY_SENSITIVE":
        return PolicyResult(
            policy_id="security-sensitive",
            action="REQUIRES_SECURITY_REVIEW",
            reason="Security-sensitive operation requires security review.",
        )

    if risk.level == "HIGH":
        return PolicyResult(
            policy_id="high-risk",
            action="REQUIRES_REVIEW",
            reason="High-risk operation requires review.",
        )

    if classification == "MODIFY":
        return PolicyResult(
            policy_id="modify-operation",
            action="REQUIRES_REVIEW",
            reason="Infrastructure modifications require review.",
        )

    if classification == "READ_ONLY":
        return PolicyResult(
            policy_id="default-read-only",
            action="ALLOW",
            reason="Read-only operation is permitted.",
        )

    return PolicyResult(
        policy_id="unmatched-classification",
        action="REQUIRES_REVIEW",
        reason="The operation has no explicit allow policy; review is required.",
    )