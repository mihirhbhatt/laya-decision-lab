from laya_labs.evidence.cloud_collector import (
    create_cloud_evidence,
)

from laya_labs.cloud.security_controls import (
    evaluate_encryption,
)

from laya_labs.grc.finding_engine import (
    create_finding,
)


class CloudSecurityPipeline:

    def evaluate_resource(self, resource):

        evidence = create_cloud_evidence(
            resource
        )

        control_result = evaluate_encryption(
            resource
        )

        finding = create_finding(
            control_result=control_result,
            resource_id=resource.resource_id,
            evidence_ids=[
                evidence.evidence_id
            ],
        )

        return {
            "resource": resource,
            "evidence": evidence,
            "control_result": control_result,
            "finding": finding,
        }