from uuid import uuid4

from laya_labs.grc.findings import Finding


def create_finding(
    control_result,
    resource_id: str,
    evidence_ids: list[str],
):

    if control_result.status != "FAIL":
        return None

    return Finding(
        finding_id=str(uuid4()),
        control_id=control_result.control_id,
        framework=control_result.framework,
        resource_id=resource_id,
        severity=control_result.severity,
        status="OPEN",
        description=control_result.message,
        evidence_ids=evidence_ids,
        recommendation=(
            "Remediate the resource so that "
            "the security control passes."
        ),
    )