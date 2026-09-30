from typing import Protocol


class LLMProvider(Protocol):

    def classify(self, request: str) -> dict:
        ...


class MockLLMProvider:

    def classify(self, request: str) -> dict:

        text = request.lower()

        if "production" in text and (
            "change" in text
            or "modify" in text
            or "delete" in text
            or "destroy" in text
        ):
            category = "MODIFY"
            confidence = 0.70

        elif (
            "read" in text
            or "inspect" in text
            or "list" in text
            or "show" in text
        ):
            category = "READ_ONLY"
            confidence = 0.85

        else:
            category = "UNKNOWN"
            confidence = 0.50

        return {
            "source": "mock-llm",
            "category": category,
            "confidence": confidence,
        }