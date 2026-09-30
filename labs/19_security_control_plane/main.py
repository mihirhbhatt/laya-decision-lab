from laya_labs.cloud.models import CloudResource
from laya_labs.cloud.security_pipeline import CloudSecurityPipeline


def main():
    resources = [
        CloudResource("disk-safe", "aws", "volume", "us-east-1", configuration={"encrypted": True}),
        CloudResource("disk-open", "aws", "volume", "us-east-1", configuration={"encrypted": False}),
    ]
    pipeline = CloudSecurityPipeline()
    for resource in resources:
        result = pipeline.evaluate_resource(resource)
        finding = result["finding"]
        print(
            f"{resource.resource_id}: {result['control_result'].status}; "
            f"finding={finding.finding_id if finding else 'none'}"
        )


if __name__ == "__main__":
    main()