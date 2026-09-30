from laya_labs.decisions.score import calculate_risk_score
from laya_labs.decisions.structured import create_decision


def policy_for_risk(risk_level: str) -> tuple[str, bool]:

    if risk_level == "CRITICAL":
        return "REQUIRES_HUMAN_APPROVAL", True

    if risk_level == "HIGH":
        return "REQUIRES_SECURITY_REVIEW", True

    if risk_level == "MEDIUM":
        return "REQUIRES_REVIEW", False

    return "ALLOW", False


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 04")
    print("STRUCTURED SECURITY DECISION")
    print("=" * 80)

    request = "Terraform destroy production"

    print()
    print("Input Request:")
    print(f"  {request}")

    # Step 1: Calculate risk
    risk = calculate_risk_score(
        destructive=True,
        production=True,
        privileged=True,
    )

    print()
    print("Risk Calculation:")
    print(f"  Score : {risk.score:.2f}")
    print(f"  Level : {risk.level}")

    # Step 2: Apply policy
    action, approval_required = policy_for_risk(
        risk.level
    )

    print()
    print("Policy Evaluation:")
    print(f"  Action            : {action}")
    print(f"  Approval required : {approval_required}")

    # Step 3: Create structured decision
    decision = create_decision(
        decision_id="DEC-0001",
        request=request,
        classification="DESTRUCTIVE",
        risk_score=risk.score,
        risk_level=risk.level,
        policy_action=action,
        reason=(
            "Destructive operation targeting "
            "production infrastructure."
        ),
        approval_required=approval_required,
        evidence=[
            "request_text",
            "operation_classification",
            "risk_factors",
        ],
        classifier_source="regex",
    )

    print()
    print("Structured Security Decision:")
    print("-" * 80)

    print(f"  Decision ID       : {decision.decision_id}")
    print(f"  Classification    : {decision.classification}")
    print(f"  Risk Score        : {decision.risk_score:.2f}")
    print(f"  Risk Level        : {decision.risk_level}")
    print(f"  Policy Action     : {decision.policy_action}")
    print(
        f"  Approval Required : "
        f"{decision.approval_required}"
    )
    print(f"  Classifier Source : {decision.classifier_source}")

    print()
    print("Reason:")
    print(f"  {decision.reason}")

    print()
    print("Evidence:")

    for item in decision.evidence:
        print(f"  - {item}")

    print()
    print("=" * 80)
    print("LAB 04 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()