from laya_labs.decisions.score import (
    calculate_risk_score,
)

from laya_labs.middleware.policy_gate import (
    policy_gate,
)

from laya_labs.middleware.redaction import (
    redact_sensitive_data,
)

from laya_labs.middleware.logging import (
    create_audit_event,
)

from laya_labs.engine.schemas import (
    Control,
    Evidence,
    ControlEvaluation,
)


def evaluate_control(
    control: Control,
    request: str,
):

    sanitized_request = redact_sensitive_data(
        request
    )

    risk = calculate_risk_score(
        destructive="destroy" in request.lower(),
        security_sensitive=(
            "iam" in request.lower()
            or "mfa" in request.lower()
            or "encryption" in request.lower()
        ),
        production="production" in request.lower(),
        privileged="admin" in request.lower(),
    )

    decision = policy_gate(
        risk.level
    )

    if decision == "ALLOW":
        status = "COMPLIANT"
    else:
        status = "REQUIRES_REVIEW"

    evidence = Evidence(
        evidence_id="EVD-0001",
        control_id=control.control_id,
        source="request-analysis",
        description=(
            "Security decision generated from request "
            "classification and risk analysis."
        ),
        status=status,
    )

    evaluation = ControlEvaluation(
        control_id=control.control_id,
        status=status,
        decision=decision,
        evidence=[evidence],
    )

    audit_event = create_audit_event(
        request=sanitized_request,
        decision=decision,
        source="enterprise-control-plane",
    )

    return evaluation, audit_event


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 10")
    print("MINI GRC SECURITY CONTROL PLANE")
    print("=" * 80)

    control = Control(
        control_id="SECCTRL-001",
        title="Privileged changes require security review",
        description=(
            "High-impact privileged infrastructure "
            "operations require controlled approval."
        ),
        framework_mappings=[
            "NIST",
            "ISO27001",
            "SOC2",
            "PCI_DSS",
        ],
    )

    request = (
        "terraform destroy production "
        "using admin credentials"
    )

    evaluation, audit_event = evaluate_control(
        control,
        request,
    )

    print()
    print("CONTROL")
    print("-" * 80)
    print(f"ID          : {control.control_id}")
    print(f"Title       : {control.title}")
    print(f"Description : {control.description}")

    print()
    print("Framework mappings:")

    for framework in control.framework_mappings:
        print(f"  - {framework}")

    print()
    print("EVALUATION")
    print("-" * 80)
    print(f"Control     : {evaluation.control_id}")
    print(f"Status      : {evaluation.status}")
    print(f"Decision    : {evaluation.decision}")

    print()
    print("EVIDENCE")
    print("-" * 80)

    for evidence in evaluation.evidence:
        print(f"Evidence ID : {evidence.evidence_id}")
        print(f"Source      : {evidence.source}")
        print(f"Description : {evidence.description}")
        print(f"Status      : {evidence.status}")

    print()
    print("AUDIT EVENT")
    print("-" * 80)

    for key, value in audit_event.items():
        print(f"{key}: {value}")

    print()
    print("=" * 80)
    print("LAB 10 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()