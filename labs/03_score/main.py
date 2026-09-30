from laya_labs.decisions.score import calculate_risk_score


def display_result(request: str, risk):
    print()
    print("-" * 80)
    print(f"Request    : {request}")
    print(f"Risk score : {risk.score:.2f}")
    print(f"Risk level : {risk.level}")

    print("Risk factors:")

    if not risk.factors:
        print("  NONE")

    for factor in risk.factors:
        print(f"  - {factor.name}")
        print(f"    Weight : {factor.weight:.2f}")
        print(f"    Reason : {factor.reason}")


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 03")
    print("RISK SCORING ENGINE")
    print("=" * 80)

    scenarios = [
        {
            "request": "List all EC2 instances.",
            "destructive": False,
            "security_sensitive": False,
            "production": False,
            "privileged": False,
            "data_exposure": False,
        },
        {
            "request": "Create an EC2 instance in development.",
            "destructive": False,
            "security_sensitive": False,
            "production": False,
            "privileged": False,
            "data_exposure": False,
        },
        {
            "request": "Disable MFA for production administrators.",
            "destructive": False,
            "security_sensitive": True,
            "production": True,
            "privileged": True,
            "data_exposure": False,
        },
        {
            "request": "Terraform destroy production.",
            "destructive": True,
            "security_sensitive": False,
            "production": True,
            "privileged": True,
            "data_exposure": False,
        },
        {
            "request": "Export production customer data.",
            "destructive": False,
            "security_sensitive": True,
            "production": True,
            "privileged": True,
            "data_exposure": True,
        },
    ]

    for scenario in scenarios:

        risk = calculate_risk_score(
            destructive=scenario["destructive"],
            security_sensitive=scenario["security_sensitive"],
            production=scenario["production"],
            privileged=scenario["privileged"],
            data_exposure=scenario["data_exposure"],
        )

        display_result(
            scenario["request"],
            risk,
        )

    print()
    print("=" * 80)
    print("LAB 03 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()