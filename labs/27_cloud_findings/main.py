from laya_labs.cloud.gcp import normalize_resource
from laya_labs.cloud.security_controls import evaluate_encryption
from laya_labs.grc.finding_engine import create_finding


def main():
    resource = normalize_resource({
        "name": "bucket-demo", "kind": "storage_bucket", "region": "us-central1",
        "configuration": {"encrypted": False},
    })
    control = evaluate_encryption(resource)
    finding = create_finding(control, resource.resource_id, ["evidence-demo"])
    print(f"Control: {control.status}; finding: {finding.finding_id if finding else 'none'}")


if __name__ == "__main__":
    main()