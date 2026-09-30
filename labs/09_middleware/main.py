from laya_labs.decisions.score import calculate_risk_score
from laya_labs.middleware.redaction import (
    redact_sensitive_data,
)
from laya_labs.middleware.policy_gate import (
    policy_gate,
)
from laya_labs.middleware.logging import (
    create_audit_event,
)


def process_request(request: str):

    sanitized = redact_sensitive_data(request)

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

    audit_event = create_audit_event(
        request=sanitized,
        decision=decision,
        source="lab-09",
    )

    return {
        "request": sanitized,
        "risk_score": risk.score,
        "risk_level": risk.level,
        "decision": decision,
        "audit_event": audit_event,
    }


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 09")
    print("ENTERPRISE MIDDLEWARE")
    print("=" * 80)

    request = (
        "terraform destroy production "
        "password=SuperSecret123"
    )

    result = process_request(request)

    print()
    print("Sanitized Request:")
    print(f"  {result['request']}")

    print()
    print("Risk:")
    print(f"  Score : {result['risk_score']:.2f}")
    print(f"  Level : {result['risk_level']}")

    print()
    print("Policy:")
    print(f"  {result['decision']}")

    print()
    print("Audit Event:")

    for key, value in result["audit_event"].items():
        print(f"  {key}: {value}")

    print()
    print("=" * 80)
    print("LAB 09 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()