from hashlib import sha256
from importlib.metadata import version
from pathlib import Path
from typing import Any

from laya.evals import ChoiceAccuracy, Dataset, EvalReport, evaluate

from laya_labs.guardrails.regex_classifier import classify_with_regex


class RegexBaselineRunner:
    def predict(
        self,
        state: Any,
        questions: dict,
        model: str | None = None,
    ) -> dict:
        request = state.get("request") if isinstance(state, dict) else state
        if not isinstance(request, str):
            raise ValueError("Evaluation state must contain request text.")
        result = classify_with_regex(request)
        return {
            "answers": {
                "operation_type": {
                    "type": "choice",
                    "choice": result.category if result else "UNKNOWN",
                    "answer_confidence": 1.0 if result else 0.0,
                }
            }
        }


def load_security_dataset(path: str | Path) -> Dataset:
    return Dataset.from_jsonl(str(path))


def evaluate_laya_vs_regex(
    dataset_path: str | Path,
    laya_router: Any,
    batch_size: int = 8,
) -> tuple[EvalReport, EvalReport]:
    dataset_file = Path(dataset_path)
    dataset = load_security_dataset(dataset_file)
    dataset_digest = sha256(dataset_file.read_bytes()).hexdigest()
    common_config = {
        "purpose": "security-request classification validation",
        "dataset": dataset_file.name,
        "dataset_sha256": dataset_digest,
        "laya_version": version("laya"),
    }
    laya_report = evaluate(
        laya_router,
        dataset,
        batch_size=batch_size,
        config={**common_config, "classifier": "laya-router"},
    )
    regex_report = evaluate(
        RegexBaselineRunner(),
        dataset,
        evaluators=[ChoiceAccuracy()],
        batch_size=batch_size,
        config={**common_config, "classifier": "regex"},
    )
    return laya_report, regex_report