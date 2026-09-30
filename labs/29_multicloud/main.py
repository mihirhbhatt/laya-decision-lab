from laya_labs.cloud.azure import normalize_resource as azure_resource
from laya_labs.cloud.gcp import normalize_resource as gcp_resource
from laya_labs.cloud.kubernetes import normalize_resource as kubernetes_resource


def main():
    resources = [
        azure_resource({"id": "vm-1", "type": "compute/vm", "location": "east"}),
        gcp_resource({"name": "bucket-1", "kind": "storage", "region": "us"}),
        kubernetes_resource({"kind": "Pod", "metadata": {"name": "api", "namespace": "apps"}}),
    ]
    for resource in resources:
        print(f"{resource.provider}: {resource.resource_type} {resource.resource_id}")


if __name__ == "__main__":
    main()