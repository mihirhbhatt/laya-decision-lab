from laya_labs.audit import AuditLog


def main():
    audit = AuditLog()
    event = audit.record(
        "POLICY_EVALUATED", "decision-demo",
        {"action": "REQUIRES_REVIEW", "api_token": "never-log-this"},
    )
    print(event)
    print(f"Recorded audit events: {len(audit.list_events())}")


if __name__ == "__main__":
    main()