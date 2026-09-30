from typing import Any

from laya_labs.cloud.models import CloudResource

FLOCI_ENDPOINT = "http://localhost:4566"
FLOCI_REGION = "us-east-1"


class AWSDiscovery:
    def __init__(
        self,
        endpoint_url: str | None = None,
        region_name: str | None = None,
        ec2_client: Any | None = None,
    ):
        self.endpoint_url = endpoint_url
        if ec2_client is None:
            import boto3

            client_options: dict[str, str] = {}
            if endpoint_url is not None:
                client_options.update(
                    aws_access_key_id="test",
                    aws_secret_access_key="test",
                )
            self.ec2 = boto3.client(
                "ec2",
                endpoint_url=endpoint_url,
                region_name=region_name,
                **client_options,
            )
        else:
            self.ec2 = ec2_client

    def seed_floci_fixture(self) -> str:
        client_endpoint = getattr(self.ec2.meta, "endpoint_url", None)
        if self.endpoint_url != FLOCI_ENDPOINT or client_endpoint != FLOCI_ENDPOINT:
            raise RuntimeError("Fixture instances can only be created in Floci.")
        response = self.ec2.run_instances(
            ImageId="ami-amazonlinux2023",
            InstanceType="t2.micro",
            MinCount=1,
            MaxCount=1,
            BlockDeviceMappings=[
                {
                    "DeviceName": "/dev/xvda",
                    "Ebs": {
                        "VolumeSize": 8,
                        "VolumeType": "gp3",
                        "Encrypted": True,
                        "DeleteOnTermination": True,
                    },
                }
            ],
            TagSpecifications=[
                {
                    "ResourceType": "instance",
                    "Tags": [{"Key": "Name", "Value": "laya-poc"}],
                }
            ],
        )
        return response["Instances"][0]["InstanceId"]

    def discover_instances(self) -> list[CloudResource]:
        response = self.ec2.describe_instances()
        instances = [
            instance
            for reservation in response.get("Reservations", [])
            for instance in reservation.get("Instances", [])
        ]
        instance_volumes: dict[str, list[str]] = {}
        volume_ids: set[str] = set()
        for instance in instances:
            ids = [
                mapping["Ebs"]["VolumeId"]
                for mapping in instance.get("BlockDeviceMappings", [])
                if mapping.get("Ebs", {}).get("VolumeId")
            ]
            instance_volumes[instance["InstanceId"]] = ids
            volume_ids.update(ids)

        volume_encryption: dict[str, bool] = {}
        sorted_volume_ids = sorted(volume_ids)
        for start in range(0, len(sorted_volume_ids), 500):
            batch = sorted_volume_ids[start:start + 500]
            volume_response = self.ec2.describe_volumes(VolumeIds=batch)
            volume_encryption.update(
                {
                    volume["VolumeId"]: volume["Encrypted"]
                    for volume in volume_response.get("Volumes", [])
                    if isinstance(volume.get("Encrypted"), bool)
                }
            )

        resources = []
        for instance in instances:
            ids = instance_volumes[instance["InstanceId"]]
            known_encryption = [volume_encryption.get(volume_id) for volume_id in ids]
            if any(value is False for value in known_encryption):
                encrypted = False
            elif known_encryption and all(isinstance(value, bool) for value in known_encryption):
                encrypted = all(known_encryption)
            else:
                encrypted = None

            resources.append(
                CloudResource(
                    resource_id=instance["InstanceId"],
                    provider="aws",
                    resource_type="ec2_instance",
                    region=self.ec2.meta.region_name,
                    configuration={
                        "state": instance["State"]["Name"],
                        "instance_type": instance["InstanceType"],
                        "volume_ids": ids,
                        "encrypted": encrypted,
                    },
                )
            )
        return resources