from laya_labs.audit import AuditLog
from laya_labs.engine.security_decision_engine import SecurityDecisionEngine


def main():
    audit = AuditLog()
    decision = SecurityDecisionEngine().evaluate(
        request="terraform destroy production", environment="production"
    )
    audit.record(
        "SECURITY_DECISION", decision.decision_id,
        {
            "request": decision.request,
            "classification": decision.classification,
            "risk": decision.risk.level,
            "policy": decision.policy.action,
            "approval": decision.approval.status,
        },
    )
    print(audit.list_events()[0])


if __name__ == "__main__":
    main()