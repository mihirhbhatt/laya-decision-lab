from laya_labs.engine.laya_engine import LayaEngine

from laya_labs.decisions.choice import (
    build_choice_question
)

from laya_labs.guardrails.hybrid_classifier import (
    HybridClassifier
)

from laya_labs.guardrails.risk_classifier import (
    apply_operation_policy
)


def main():

    engine = LayaEngine()

    classifier = HybridClassifier(engine)

    questions = build_choice_question(
        "operation_type",

        "What type of infrastructure operation is being requested?",

        {
            "READ_ONLY":
                "Reads, lists, describes, queries, or audits resources.",

            "MODIFY":
                "Creates, updates, configures, deploys, or changes infrastructure.",

            "DESTRUCTIVE":
                "Deletes, destroys, terminates, removes, or tears down infrastructure.",

            "SECURITY_SENSITIVE":
                "Changes IAM, permissions, encryption, logging, security controls, or credentials.",
        }
    )

    requests = [

        "List all EC2 instances.",

        "Create a new EC2 instance.",

        "terraform destroy production.",

        "Disable MFA for IAM users.",

        "Grant administrator permissions.",

        "Can you tear down our live environment?",

        "What resources are currently deployed?",

        "Please make the development server bigger.",

        "Can you inspect the current AWS environment?",
    ]

    print("=" * 80)
    print("LAB 02 - CHOICE + REGEX + LAYA")
    print("=" * 80)

    for request in requests:

        decision = classifier.classify(
            request,
            questions
        )

        policy = apply_operation_policy(
            decision["category"]
        )

        print()
        print("-" * 80)

        print("Request      :", request)
        print("Classifier   :", decision["source"])
        print("Category     :", decision["category"])
        print("Confidence   :", decision["confidence"])
        print("Policy       :", policy)
        print("Laya used    :", decision["requires_laya"])

        if decision["matched_pattern"]:
            print(
                "Regex        :",
                decision["matched_pattern"]
            )


if __name__ == "__main__":
    main()