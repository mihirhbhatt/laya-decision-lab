from laya_labs.cloud.azure import normalize_resource
from laya_labs.evidence import collect_evidence


def main():
    resource = normalize_resource({
        "id": "vm-demo", "type": "compute/virtualMachines",
        "location": "westus", "properties": {"encrypted": True},
    })
    evidence = collect_evidence(
        resource.provider, resource.resource_type, resource.resource_id,
        {"region": resource.region, "configuration": resource.configuration},
    )
    print(f"Collected {evidence.evidence_type} from {evidence.source}: {evidence.evidence_id}")


if __name__ == "__main__":
    main()