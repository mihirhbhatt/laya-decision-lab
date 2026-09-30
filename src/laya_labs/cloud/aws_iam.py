import boto3

from laya_labs.cloud.models import CloudResource


class AWSDiscovery:

    def __init__(self):
        self.ec2 = boto3.client("ec2")

    def discover_instances(self):

        response = self.ec2.describe_instances()

        resources = []

        for reservation in response["Reservations"]:

            for instance in reservation["Instances"]:

                resources.append(
                    CloudResource(
                        resource_id=instance["InstanceId"],
                        provider="aws",
                        resource_type="ec2_instance",
                        region=self.ec2.meta.region_name,
                        configuration={
                            "state": instance[
                                "State"
                            ]["Name"],
                            "instance_type": instance[
                                "InstanceType"
                            ],
                        },
                    )
                )

        return resources