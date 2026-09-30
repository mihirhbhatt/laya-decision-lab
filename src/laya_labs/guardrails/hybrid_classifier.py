from laya_labs.guardrails.regex_classifier import (
    classify_with_regex
)


class HybridClassifier:

    def __init__(self, laya_engine):
        self.laya_engine = laya_engine

    def classify(self, request, questions):

        regex_result = classify_with_regex(request)

        if regex_result:

            return {
                "source": "regex",
                "category": regex_result.category,
                "confidence": regex_result.rule_confidence,
                "matched_pattern": regex_result.matched_pattern,
                "requires_laya": False,
            }

        result = self.laya_engine.predict(
            request,
            questions
        )

        answer = result["answers"]["operation_type"]

        return {
            "source": "laya",
            "category": answer["choice"],
            "confidence": answer.get("answer_confidence"),
            "matched_pattern": None,
            "requires_laya": True,
        }