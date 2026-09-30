from laya_labs.guardrails.regex_classifier import (
    classify_with_regex,
)

VALID_CLASSIFICATIONS = {
    "READ_ONLY",
    "MODIFY",
    "SECURITY_SENSITIVE",
    "DESTRUCTIVE",
    "DATA_ACCESS",
    "PRIVILEGED",
    "UNKNOWN",
}


class DecisionPipeline:

    def __init__(
        self,
        laya_engine=None,
        llm_provider=None,
        confidence_threshold: float = 0.80,
    ):
        if not 0.0 <= confidence_threshold <= 1.0:
            raise ValueError("confidence_threshold must be between 0 and 1.")
        self.laya_engine = laya_engine
        self.llm_provider = llm_provider
        self.confidence_threshold = confidence_threshold

    def classify(self, request: str, laya_questions=None):
        if not isinstance(request, str) or not request.strip():
            raise ValueError("request must be non-empty text.")

        regex_result = classify_with_regex(request)
        if regex_result:
            return {
                "source": "regex",
                "category": regex_result.category,
                "confidence": regex_result.rule_confidence,
                "matched_pattern": regex_result.matched_pattern,
            }

        laya_candidate = None
        if self.laya_engine and laya_questions:
            try:
                result = self.laya_engine.predict(request, laya_questions)
                answer = result["answers"]["operation_type"]
                laya_candidate = self._normalize(
                    "laya",
                    answer.get("choice"),
                    answer.get("answer_confidence"),
                )
                if laya_candidate["category"] != "UNKNOWN":
                    return laya_candidate
            except Exception:
                laya_candidate = None

        llm_candidate = None
        if self.llm_provider:
            try:
                result = self.llm_provider.classify(request)
                llm_candidate = self._normalize(
                    "llm",
                    result.get("category") if isinstance(result, dict) else None,
                    result.get("confidence") if isinstance(result, dict) else None,
                )
                if llm_candidate["category"] != "UNKNOWN":
                    return llm_candidate
            except Exception:
                llm_candidate = None

        return llm_candidate or laya_candidate or {
            "source": "none",
            "category": "UNKNOWN",
            "confidence": 0.0,
        }

    def _normalize(self, source: str, category, confidence) -> dict:
        valid_confidence = (
            isinstance(confidence, (int, float))
            and not isinstance(confidence, bool)
            and 0.0 <= confidence <= 1.0
        )
        confidence = float(confidence) if valid_confidence else 0.0
        if category not in VALID_CLASSIFICATIONS or category == "UNKNOWN":
            return {"source": source, "category": "UNKNOWN", "confidence": confidence}
        if confidence < self.confidence_threshold:
            return {
                "source": source,
                "category": "UNKNOWN",
                "confidence": confidence,
                "candidate_category": category,
            }
        return {"source": source, "category": category, "confidence": confidence}