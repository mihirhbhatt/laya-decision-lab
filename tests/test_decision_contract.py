import pytest

from laya_labs.engine.security_decision_engine import SecurityDecisionEngine
from laya_labs.policy.engine import calculate_risk


class FakeLaya:
    def __init__(self, category, confidence):
        self.category = category
        self.confidence = confidence
        self.calls = 0

    def predict(self, request, questions):
        self.calls += 1
        assert "operation_type" in questions
        return {
            "answers": {
                "operation_type": {
                    "choice": self.category,
                    "answer_confidence": self.confidence,
                }
            }
        }


class FakeLLM:
    def __init__(self, category, confidence, policy_action=None):
        self.category = category
        self.confidence = confidence
        self.policy_action = policy_action
        self.calls = 0

    def classify(self, request):
        self.calls += 1
        result = {
            "source": "test-llm",
            "category": self.category,
            "confidence": self.confidence,
        }
        if self.policy_action is not None:
            result["policy_action"] = self.policy_action
        return result


@pytest.mark.parametrize("raw_input", ["", "   ", "a" * 2001, None])
def test_request_validation_rejects_blank_non_text_and_oversized_input(raw_input):
    with pytest.raises(ValueError):
        SecurityDecisionEngine().evaluate(raw_input)


def test_environment_is_normalized_and_unknown_values_are_rejected():
    engine = SecurityDecisionEngine()

    decision = engine.evaluate("terraform destroy", environment=" Production ")

    assert decision.metadata["environment"] == "production"
    assert decision.policy.action == "REQUIRES_HUMAN_APPROVAL"
    with pytest.raises(ValueError, match="environment"):
        engine.evaluate("List instances", environment="sandbox")


@pytest.mark.parametrize(
    ("privileged", "data_exposure"),
    [("yes", False), (False, 1)],
)
def test_context_flags_must_be_booleans(privileged, data_exposure):
    with pytest.raises(ValueError, match="boolean"):
        SecurityDecisionEngine().evaluate(
            "List instances",
            privileged=privileged,
            data_exposure=data_exposure,
        )


def test_regex_classification_runs_before_models():
    laya = FakeLaya("READ_ONLY", 1.0)
    llm = FakeLLM("READ_ONLY", 1.0)
    engine = SecurityDecisionEngine(laya_engine=laya, llm_provider=llm)

    decision = engine.evaluate("terraform destroy", environment="production")

    assert decision.source == "regex"
    assert decision.classification == "DESTRUCTIVE"
    assert decision.policy.action == "REQUIRES_HUMAN_APPROVAL"
    assert laya.calls == 0
    assert llm.calls == 0


def test_high_confidence_laya_classification_is_normalized_and_reviewed():
    laya = FakeLaya("MODIFY", 0.95)
    llm = FakeLLM("READ_ONLY", 1.0)
    engine = SecurityDecisionEngine(laya_engine=laya, llm_provider=llm)

    decision = engine.evaluate("adjust the service topology")

    assert decision.source == "laya"
    assert decision.classification == "MODIFY"
    assert decision.policy.action == "REQUIRES_REVIEW"
    assert llm.calls == 0


def test_laya_confidence_threshold_is_inclusive():
    decision = SecurityDecisionEngine(
        laya_engine=FakeLaya("MODIFY", 0.80)
    ).evaluate("adjust the service topology")

    assert decision.source == "laya"
    assert decision.classification == "MODIFY"


def test_laya_below_threshold_remains_unknown_without_fallback():
    decision = SecurityDecisionEngine(
        laya_engine=FakeLaya("MODIFY", 0.79)
    ).evaluate("adjust the service topology")

    assert decision.classification == "UNKNOWN"
    assert decision.metadata["candidate_category"] == "MODIFY"
    assert decision.policy.action == "REQUIRES_REVIEW"


def test_low_confidence_laya_falls_back_to_llm_classifier():
    laya = FakeLaya("UNKNOWN", 0.49)
    llm = FakeLLM("DESTRUCTIVE", 0.90)
    engine = SecurityDecisionEngine(laya_engine=laya, llm_provider=llm)

    decision = engine.evaluate("retire the obsolete service")

    assert decision.source == "llm"
    assert decision.classification == "DESTRUCTIVE"
    assert decision.policy.action == "REQUIRES_REVIEW"
    assert laya.calls == 1
    assert llm.calls == 1


def test_invalid_model_category_fails_closed():
    decision = SecurityDecisionEngine(
        llm_provider=FakeLLM("HIGH_IMPACT", 0.99)
    ).evaluate("perform an unfamiliar operation")

    assert decision.classification == "UNKNOWN"
    assert decision.policy.action == "REQUIRES_REVIEW"


def test_model_classified_read_only_does_not_create_an_automatic_allow():
    decision = SecurityDecisionEngine(
        llm_provider=FakeLLM("READ_ONLY", 0.99, policy_action="ALLOW")
    ).evaluate("inspect the service topology")

    assert decision.classification == "READ_ONLY"
    assert decision.source == "llm"
    assert decision.policy.action == "REQUIRES_REVIEW"


def test_classifier_failures_remain_unknown_and_require_review():
    class BrokenLaya:
        def predict(self, request, questions):
            raise RuntimeError("provider unavailable")

    class BrokenLLM:
        def classify(self, request):
            raise RuntimeError("provider unavailable")

    decision = SecurityDecisionEngine(
        laya_engine=BrokenLaya(),
        llm_provider=BrokenLLM(),
    ).evaluate("inspect the service topology")

    assert decision.source == "none"
    assert decision.classification == "UNKNOWN"
    assert decision.policy.action == "REQUIRES_REVIEW"


def test_decision_includes_structured_classification_risk_and_policy_evidence():
    decision = SecurityDecisionEngine().evaluate("List EC2 instances")

    assert [item["type"] for item in decision.evidence] == [
        "classification",
        "risk_assessment",
        "policy_evaluation",
    ]


def test_risk_threshold_boundaries_are_deterministic():
    medium = calculate_risk("MODIFY", "production")
    high = calculate_risk("DESTRUCTIVE", "production")

    assert medium.score == pytest.approx(0.30)
    assert medium.level == "MEDIUM"
    assert high.score == pytest.approx(0.60)
    assert high.level == "HIGH"


def test_critical_production_destroy_is_blocked_before_approval():
    decision = SecurityDecisionEngine().evaluate(
        "terraform destroy",
        environment="production",
        privileged=True,
        data_exposure=True,
    )

    assert decision.risk.level == "CRITICAL"
    assert decision.policy.action == "BLOCK"
    assert decision.approval.status == "NOT_REQUIRED"