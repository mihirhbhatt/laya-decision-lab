from pathlib import Path

from laya_labs.policy import ConfiguredPolicyEngine, load_policy_rules


def main():
    policy_file = Path(__file__).resolve().parents[2] / "policies/phase2/risk-policy.yaml"
    engine = ConfiguredPolicyEngine(load_policy_rules(policy_file))
    for classification, environment in (
        ("READ_ONLY", "production"),
        ("DESTRUCTIVE", "production"),
        ("UNKNOWN", "development"),
    ):
        result = engine.evaluate(classification, environment)
        print(f"{classification} @ {environment}: {result.action} ({result.policy_id})")


if __name__ == "__main__":
    main()