from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4

from laya_labs.audit.events import AuditEvent

_SENSITIVE_PARTS = ("password", "secret", "token", "credential", "private_key")


def _redact(value):
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if any(part in str(key).lower() for part in _SENSITIVE_PARTS)
            else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class AuditLog:
    def __init__(self):
        self._events: list[AuditEvent] = []

    def record(
        self,
        event_type: str,
        decision_id: str,
        payload: dict | None = None,
    ) -> AuditEvent:
        if not event_type or not decision_id:
            raise ValueError("Audit event type and decision ID are required.")
        event = AuditEvent(
            event_id=str(uuid4()),
            timestamp=datetime.now(timezone.utc),
            event_type=event_type,
            decision_id=decision_id,
            payload=_redact(deepcopy(payload or {})),
        )
        self._events.append(event)
        return event

    def list_events(self) -> list[AuditEvent]:
        return list(self._events)