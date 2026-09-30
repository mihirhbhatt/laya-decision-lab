from laya_labs.cloud.drift import compare_resources
from laya_labs.cloud.models import CloudResource


def main():
    expected = CloudResource("bucket-demo", "aws", "bucket", "us-east-1", configuration={"encrypted": True})
    observed = CloudResource("bucket-demo", "aws", "bucket", "us-east-1", configuration={"encrypted": False})
    differences = compare_resources(observed, expected)
    print(f"Drifted fields: {', '.join(differences) if differences else 'none'}")


if __name__ == "__main__":
    main()