from laya_labs.cloud.models import CloudResource


def normalize_resource(resource: dict) -> CloudResource:
    return CloudResource(
        resource_id=str(resource["id"]),
        provider="azure",
        resource_type=str(resource["type"]),
        region=str(resource.get("location", "unknown")),
        tags=dict(resource.get("tags") or {}),
        configuration=dict(resource.get("properties") or {}),
    )