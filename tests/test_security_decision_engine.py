from laya_labs.engine.security_decision_engine import SecurityDecisionEngine


def test_read_only_request_is_allowed_without_approval():
    decision = SecurityDecisionEngine().evaluate(
        "List EC2 instances", environment="development"
    )

    assert decision.classification == "READ_ONLY"
    assert decision.policy.action == "ALLOW"
    assert decision.approval.status == "NOT_REQUIRED"


def test_modify_request_requires_review():
    decision = SecurityDecisionEngine().evaluate(
        "Create an EC2 instance", environment="development"
    )

    assert decision.classification == "MODIFY"
    assert decision.policy.action == "REQUIRES_REVIEW"
    assert decision.approval.status == "PENDING"


def test_production_destroy_requires_human_approval():
    decision = SecurityDecisionEngine().evaluate(
        "terraform destroy", environment="production"
    )

    assert decision.classification == "DESTRUCTIVE"
    assert decision.risk.level == "HIGH"
    assert decision.policy.action == "REQUIRES_HUMAN_APPROVAL"
    assert decision.approval.status == "PENDING"


def test_development_destroy_still_requires_review():
    decision = SecurityDecisionEngine().evaluate(
        "terraform destroy", environment="development"
    )

    assert decision.policy.action == "REQUIRES_REVIEW"
    assert decision.approval.required is True


def test_security_sensitive_request_requires_security_review():
    decision = SecurityDecisionEngine().evaluate(
        "disable MFA", environment="production"
    )

    assert decision.classification == "SECURITY_SENSITIVE"
    assert decision.policy.action == "REQUIRES_SECURITY_REVIEW"
    assert decision.approval.status == "PENDING"


def test_unknown_request_requires_review_instead_of_implicit_allow():
    decision = SecurityDecisionEngine().evaluate(
        "calculate the moonbeam index", environment="development"
    )

    assert decision.classification == "UNKNOWN"
    assert decision.policy.action == "REQUIRES_REVIEW"
    assert decision.approval.status == "PENDING"


def test_privileged_context_requires_human_approval():
    decision = SecurityDecisionEngine().evaluate(
        "read configuration", privileged=True
    )

    assert "privileged_operation" in decision.risk.factors
    assert decision.policy.action == "REQUIRES_HUMAN_APPROVAL"


def test_data_exposure_context_requires_security_review():
    decision = SecurityDecisionEngine().evaluate(
        "read customer data", data_exposure=True
    )

    assert "data_exposure" in decision.risk.factors
    assert decision.policy.action == "REQUIRES_SECURITY_REVIEW"