from laya_labs.guardrails.regex_classifier import (
    classify_with_regex,
)
from laya_labs.routing.model_router import ModelRouter


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 06")
    print("POLICY-BASED DYNAMIC ROUTING")
    print("=" * 80)

    router = ModelRouter()

    requests = [
        "terraform destroy production",
        "List all EC2 instances",
        "What resources should we review?",
        "Please inspect infrastructure",
    ]

    for request in requests:

        regex_result = classify_with_regex(request)

        decision = router.route(
            regex_match=regex_result is not None
        )

        print()
        print("-" * 80)
        print(f"Request : {request}")
        print(f"Route   : {decision.route}")
        print(f"Reason  : {decision.reason}")

    print()
    print("=" * 80)
    print("LAB 06 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()