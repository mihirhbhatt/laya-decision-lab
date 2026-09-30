from laya_labs.audit import AuditLog
from laya_labs.cloud.azure import normalize_resource as azure_resource
from laya_labs.cloud.gcp import normalize_resource as gcp_resource
from laya_labs.cloud.security_pipeline import CloudSecurityPipeline


def main():
    resources = [
        azure_resource({"id": "disk-a", "type": "disk", "location": "east", "properties": {"encrypted": True}}),
        gcp_resource({"name": "disk-g", "kind": "disk", "region": "us", "configuration": {"encrypted": False}}),
    ]
    pipeline = CloudSecurityPipeline()
    audit = AuditLog()
    for resource in resources:
        result = pipeline.evaluate_resource(resource)
        audit.record("CLOUD_CONTROL_EVALUATED", result["evidence"].evidence_id, {
            "provider": resource.provider,
            "resource_id": resource.resource_id,
            "control_status": result["control_result"].status,
            "finding_id": result["finding"].finding_id if result["finding"] else None,
        })
    for event in audit.list_events():
        print(event)


if __name__ == "__main__":
    main()