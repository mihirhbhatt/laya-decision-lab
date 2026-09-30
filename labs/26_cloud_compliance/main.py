from laya_labs.cloud.azure import normalize_resource
from laya_labs.cloud.security_controls import evaluate_encryption


def main():
    resource = normalize_resource({
        "id": "storage-demo", "type": "storage/account",
        "location": "westus", "properties": {"encrypted": True},
    })
    result = evaluate_encryption(resource)
    print(f"{resource.provider} resource {resource.resource_id}: {result.status}")


if __name__ == "__main__":
    main()