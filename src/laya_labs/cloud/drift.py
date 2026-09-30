from laya_labs.cloud.models import CloudResource


def compare_resources(
    observed: CloudResource,
    expected: CloudResource,
) -> list[str]:
    if (observed.provider, observed.resource_id) != (
        expected.provider,
        expected.resource_id,
    ):
        raise ValueError("Resources must identify the same provider resource.")
    differences = []
    for field in ("resource_type", "region", "tags", "configuration"):
        if getattr(observed, field) != getattr(expected, field):
            differences.append(field)
    return differences