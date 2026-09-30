import argparse

from laya_labs.cloud.aws import AWSDiscovery
from laya_labs.cloud.security_pipeline import (
    CloudSecurityPipeline,
)


def main():
    parser = argparse.ArgumentParser(description="Read-only AWS discovery or local Floci POC.")
    parser.add_argument("--floci", action="store_true", help="Use only Floci at localhost:4566.")
    parser.add_argument("--seed", action="store_true", help="Create a local encrypted demo instance if Floci is empty.")
    parser.add_argument("--region", default="us-east-1")
    args = parser.parse_args()

    if args.seed and not args.floci:
        parser.error("--seed is only allowed with --floci.")

    discovery = AWSDiscovery(
        endpoint_url="http://localhost:4566" if args.floci else None,
        region_name=args.region,
    )

    if args.seed and not discovery.discover_instances():
        instance_id = discovery.seed_floci_fixture()
        print(f"Seeded local Floci instance: {instance_id}")

    resources = discovery.discover_instances()

    pipeline = CloudSecurityPipeline()

    print()
    print("=" * 80)
    print("AWS SECURITY DISCOVERY")
    print("=" * 80)
    if args.floci:
        print("Endpoint: http://localhost:4566 (Floci; dummy credentials)")

    print(
        f"Discovered resources: "
        f"{len(resources)}"
    )

    for resource in resources:

        result = pipeline.evaluate_resource(
            resource
        )

        print()
        print("-" * 80)

        print(
            "Resource:",
            resource.resource_id,
        )

        print(
            "Type:",
            resource.resource_type,
        )

        print(
            "Region:",
            resource.region,
        )

        print(
            "Control:",
            result[
                "control_result"
            ].control_id,
        )

        print(
            "Status:",
            result[
                "control_result"
            ].status,
        )

        print(
            "EBS encryption:",
            resource.configuration["encrypted"]
            if resource.configuration["encrypted"] is not None
            else "UNKNOWN",
        )

        print("Evidence ID:", result["evidence"].evidence_id)

        if result["finding"]:

            print(
                "Finding:",
                result[
                    "finding"
                ].finding_id,
            )
        else:
            print("Finding: none")


if __name__ == "__main__":
    main()