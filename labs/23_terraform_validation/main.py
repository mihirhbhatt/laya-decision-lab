from laya_labs.cloud.terraform import TerraformAnalyzer


def main():
    plan = {
        "resource_changes": [
            {"address": "aws_instance.web", "change": {"actions": ["delete"]}},
            {"address": "aws_s3_bucket.logs", "change": {"actions": ["update"]}},
        ]
    }
    result = TerraformAnalyzer().validate_plan(plan, environment="production")
    print(f"Changes: {len(result['changes'])}; destructive: {result['destructive']}")
    print(f"Policy: {result['policy_action']}; plan was not applied.")


if __name__ == "__main__":
    main()