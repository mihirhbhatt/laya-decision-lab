from laya_labs.cloud.models import CloudResource
from laya_labs.cloud.security_pipeline import CloudSecurityPipeline


def main():
    fixture = CloudResource(
        "volume-demo", "aws", "ebs_volume", "us-east-1",
        configuration={"encrypted": False},
    )
    result = CloudSecurityPipeline().evaluate_resource(fixture)
    print(f"Encryption control: {result['control_result'].status}")
    print(f"Finding created: {result['finding'] is not None}")


if __name__ == "__main__":
    main()