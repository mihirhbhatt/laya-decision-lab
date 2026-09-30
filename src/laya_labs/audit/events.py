from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class AuditEvent:
    event_id: str
    timestamp: datetime
    event_type: str
    decision_id: str
    payload: dict[str, Any] = field(default_factory=dict)