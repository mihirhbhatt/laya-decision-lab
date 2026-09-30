from types import SimpleNamespace

import pytest

from laya_labs.cloud.aws import AWSDiscovery, FLOCI_ENDPOINT
from laya_labs.cloud.models import CloudResource
from laya_labs.cloud.security_controls import evaluate_encryption
from laya_labs.cloud.security_pipeline import CloudSecurityPipeline


class FakeEC2:
    meta = SimpleNamespace(
        region_name="us-east-1",
        endpoint_url=FLOCI_ENDPOINT,
    )

    def __init__(self, volumes):
        self.volumes = volumes
        self.run_instances_calls = 0
        self.run_instances_arguments = []

    def describe_instances(self):
        return {
            "Reservations": [
                {
                    "Instances": [
                        {
                            "InstanceId": "i-demo",
                            "State": {"Name": "running"},
                            "InstanceType": "t2.micro",
                            "BlockDeviceMappings": [
                                {"Ebs": {"VolumeId": "vol-root"}}
                            ],
                        }
                    ]
                }
            ]
        }

    def describe_volumes(self, VolumeIds):
        return {"Volumes": self.volumes}

    def run_instances(self, **kwargs):
        self.run_instances_calls += 1
        self.run_instances_arguments.append(kwargs)
        return {"Instances": [{"InstanceId": "i-local"}]}


def test_discovery_reads_attached_volume_encryption():
    discovery = AWSDiscovery(
        ec2_client=FakeEC2([{"VolumeId": "vol-root", "Encrypted": True}])
    )

    resource = discovery.discover_instances()[0]

    assert resource.configuration["encrypted"] is True
    assert resource.configuration["volume_ids"] == ["vol-root"]
    assert evaluate_encryption(resource).status == "PASS"
    result = CloudSecurityPipeline().evaluate_resource(resource)
    assert result["control_result"].status == "PASS"
    assert result["finding"] is None
    assert result["evidence"].data["configuration"]["encrypted"] is True


def test_unknown_volume_encryption_is_not_reported_as_failure():
    discovery = AWSDiscovery(ec2_client=FakeEC2([]))

    resource = discovery.discover_instances()[0]

    assert resource.configuration["encrypted"] is None
    assert evaluate_encryption(resource).status == "UNKNOWN"


def test_floci_fixture_cannot_be_seeded_without_local_endpoint():
    client = FakeEC2([])
    discovery = AWSDiscovery(ec2_client=client)

    with pytest.raises(RuntimeError, match="only be created in Floci"):
        discovery.seed_floci_fixture()

    assert client.run_instances_calls == 0


def test_floci_fixture_requests_encrypted_volume():
    client = FakeEC2([])
    discovery = AWSDiscovery(endpoint_url=FLOCI_ENDPOINT, ec2_client=client)

    assert discovery.seed_floci_fixture() == "i-local"
    assert client.run_instances_arguments[0]["BlockDeviceMappings"][0]["Ebs"]["Encrypted"] is True


def test_floci_seed_rejects_client_pointing_to_real_aws():
    client = FakeEC2([])
    client.meta.endpoint_url = "https://ec2.us-east-1.amazonaws.com"
    discovery = AWSDiscovery(endpoint_url=FLOCI_ENDPOINT, ec2_client=client)

    with pytest.raises(RuntimeError, match="only be created in Floci"):
        discovery.seed_floci_fixture()

    assert client.run_instances_calls == 0


def test_unobserved_encryption_is_unknown():
    resource = CloudResource("i-no-data", "aws", "ec2_instance", "us-east-1")

    assert evaluate_encryption(resource).status == "UNKNOWN"