from laya_labs.grc.evaluator import ControlEvaluator
from laya_labs.grc.finding_engine import create_finding


def main():
    result = ControlEvaluator().evaluate_mfa("AC-2-MFA", mfa_enabled=False)
    finding = create_finding(result, "iam-user-demo", ["evidence-demo"])
    print(f"Control {result.control_id}: {result.status}")
    print(f"Finding: {finding.finding_id if finding else 'none'}")


if __name__ == "__main__":
    main()