from pathlib import Path

import pytest

from laya_labs.policy import ConfiguredPolicyEngine, load_policy_rules

ROOT = Path(__file__).resolve().parents[1]


def test_configured_policy_requires_approval_for_production_destroy():
    rules = load_policy_rules(ROOT / "policies/phase2/risk-policy.yaml")
    result = ConfiguredPolicyEngine(rules).evaluate("DESTRUCTIVE", "production")

    assert result.action == "REQUIRES_HUMAN_APPROVAL"
    assert result.policy_id == "production-destructive"


def test_configured_policy_fails_closed_for_unmatched_request():
    engine = ConfiguredPolicyEngine([])

    result = engine.evaluate("UNKNOWN", "development")

    assert result.action == "REQUIRES_REVIEW"


def test_configured_policy_does_not_allow_model_classified_read_only():
    rules = load_policy_rules(ROOT / "policies/phase2/risk-policy.yaml")
    engine = ConfiguredPolicyEngine(rules)

    result = engine.evaluate(
        "READ_ONLY", "production", classification_source="llm"
    )

    assert result.action == "REQUIRES_REVIEW"


def test_policy_loader_rejects_unknown_action(tmp_path):
    policy_file = tmp_path / "invalid.yaml"
    policy_file.write_text(
        "version: 1\nrules:\n  - policy_id: unsafe\n    action: EXECUTE\n    reason: invalid\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Unsupported policy action"):
        load_policy_rules(policy_file)