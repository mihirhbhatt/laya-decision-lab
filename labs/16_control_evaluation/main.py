from datetime import datetime

from laya_labs.evidence.models import Evidence
from laya_labs.grc.evaluator import ControlEvaluator
from laya_labs.grc.finding_engine import create_finding


def main():

    resource_id = "aws-account-demo"

    evidence = Evidence(
        evidence_id="ev-001",
        source="aws",
        evidence_type="iam_configuration",
        resource_id=resource_id,
        collected_at=datetime.utcnow(),
        data={
            "mfa_enabled": False
        },
    )

    evaluator = ControlEvaluator()

    result = evaluator.evaluate_mfa(
        control_id="AC-MFA-001",
        mfa_enabled=evidence.data["mfa_enabled"],
    )

    finding = create_finding(
        control_result=result,
        resource_id=resource_id,
        evidence_ids=[
            evidence.evidence_id
        ],
    )

    print()
    print("=" * 80)
    print("GRC CONTROL EVALUATION")
    print("=" * 80)

    print("Control:", result.control_id)
    print("Framework:", result.framework)
    print("Status:", result.status)
    print("Severity:", result.severity)

    if finding:

        print()
        print("FINDING CREATED")
        print("Finding ID:", finding.finding_id)
        print("Status:", finding.status)
        print("Description:", finding.description)
        print("Recommendation:", finding.recommendation)


if __name__ == "__main__":
    main()