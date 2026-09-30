from laya_labs.cloud.kubernetes import normalize_resource, validate_workload_security


def main():
    workload = normalize_resource({
        "kind": "Pod",
        "metadata": {"name": "demo", "namespace": "apps"},
        "spec": {"hostNetwork": True, "containers": [{"name": "web", "securityContext": {"privileged": True}}]},
    })
    findings = validate_workload_security(workload)
    print(f"Workload: {workload.resource_id}; issues: {', '.join(findings)}")


if __name__ == "__main__":
    main()