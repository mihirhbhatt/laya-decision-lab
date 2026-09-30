from datetime import datetime, timezone
from uuid import uuid4

from laya_labs.evidence.models import Evidence


def collect_evidence(
    source: str,
    evidence_type: str,
    resource_id: str,
    data: dict,
) -> Evidence:
    if not source or not evidence_type or not resource_id:
        raise ValueError("Evidence source, type, and resource are required.")
    return Evidence(
        evidence_id=str(uuid4()),
        source=source,
        evidence_type=evidence_type,
        resource_id=resource_id,
        collected_at=datetime.now(timezone.utc),
        data=dict(data),
    )