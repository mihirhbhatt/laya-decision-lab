from laya_labs.engine.decision_pipeline import (
    DecisionPipeline,
)
from laya_labs.integrations.llm import MockLLMProvider


def main():

    print()
    print("=" * 80)
    print("LAYA DECISION LAB 05")
    print("DECISION INTELLIGENCE")
    print("=" * 80)

    pipeline = DecisionPipeline(
        llm_provider=MockLLMProvider()
    )

    requests = [
        "terraform destroy production",
        "List all EC2 instances",
        "Please inspect the production environment",
        "Do something unusual with the infrastructure",
    ]

    for request in requests:

        result = pipeline.classify(request)

        print()
        print("-" * 80)
        print(f"Request    : {request}")
        print(f"Source     : {result['source']}")
        print(f"Category   : {result['category']}")
        print(f"Confidence: {result['confidence']}")

    print()
    print("=" * 80)
    print("LAB 05 COMPLETE")
    print("=" * 80)


if __name__ == "__main__":
    main()