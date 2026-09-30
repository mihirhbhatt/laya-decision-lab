from pprint import pprint

from laya_labs.engine.security_decision_engine import (
    SecurityDecisionEngine,
)


def main():

    engine = SecurityDecisionEngine()

    requests = [
        (
            "List all EC2 instances",
            "production",
        ),
        (
            "Create a new EC2 instance",
            "development",
        ),
        (
            "Disable MFA for IAM users",
            "production",
        ),
        (
            "terraform destroy production",
            "production",
        ),
    ]

    for request, environment in requests:

        decision = engine.evaluate(
            request=request,
            environment=environment,
        )

        print()
        print("=" * 80)
        print("REQUEST")
        print(request)

        print()
        print("CLASSIFICATION")
        print(decision.classification)

        print()
        print("RISK")
        print(decision.risk.level)
        print(decision.risk.score)

        print()
        print("POLICY")
        print(decision.policy.action)

        print()
        print("APPROVAL")
        print(decision.approval.status)

        print()
        pprint(decision)


if __name__ == "__main__":
    main()