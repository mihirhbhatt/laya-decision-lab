from laya_labs.cloud.models import CloudResource


def normalize_resource(resource: dict) -> CloudResource:
    return CloudResource(
        resource_id=str(resource["name"]),
        provider="gcp",
        resource_type=str(resource["kind"]),
        region=str(resource.get("region", "unknown")),
        tags=dict(resource.get("labels") or {}),
        configuration=dict(resource.get("configuration") or {}),
    )