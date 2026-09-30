from datetime import datetime, timezone
from uuid import uuid4

from laya_labs.evidence.models import Evidence


def create_cloud_evidence(
    resource,
    source: str = "aws",
):

    return Evidence(
        evidence_id=str(uuid4()),
        source=source,
        evidence_type=resource.resource_type,
        resource_id=resource.resource_id,
        collected_at=datetime.now(timezone.utc),
        data={
            "provider": resource.provider,
            "region": resource.region,
            "configuration": resource.configuration,
            "tags": resource.tags,
        },
    )