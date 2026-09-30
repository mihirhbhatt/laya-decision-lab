from datetime import datetime, timezone


def create_audit_event(
    *,
    request: str,
    decision: str,
    source: str,
) -> dict:

    return {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        "request": request,
        "decision": decision,
        "source": source,
    }