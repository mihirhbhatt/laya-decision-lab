from laya_labs.cloud.models import CloudResource


def normalize_resource(resource: dict) -> CloudResource:
    metadata = resource.get("metadata") or {}
    spec = resource.get("spec") or {}
    return CloudResource(
        resource_id=f"{metadata.get('namespace', 'default')}/{metadata['name']}",
        provider="kubernetes",
        resource_type=str(resource["kind"]),
        region=str(resource.get("cluster", "unknown")),
        tags=dict(metadata.get("labels") or {}),
        configuration=dict(spec),
    )


def validate_workload_security(resource: CloudResource) -> list[str]:
    spec = resource.configuration
    pod_spec = spec.get("template", {}).get("spec", spec)
    findings = []
    if pod_spec.get("hostNetwork"):
        findings.append("host_network_enabled")
    for container in pod_spec.get("containers", []):
        security_context = container.get("securityContext", {})
        if security_context.get("privileged"):
            findings.append(f"privileged_container:{container.get('name', 'unnamed')}")
        if not security_context.get("runAsNonRoot"):
            findings.append(f"run_as_root_possible:{container.get('name', 'unnamed')}")
    return findings