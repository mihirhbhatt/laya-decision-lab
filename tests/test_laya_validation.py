from pathlib import Path

from laya.evals import ChoiceAccuracy, Dataset, evaluate

from laya_labs.evaluation import RegexBaselineRunner, evaluate_laya_vs_regex

ROOT = Path(__file__).resolve().parents[1]
DATASET = ROOT / "research/evals/laya_security_classification.jsonl"


def test_laya_benchmark_is_a_valid_balanced_labeled_dataset():
    dataset = Dataset.from_jsonl(str(DATASET))
    labels = [example.expected["operation_type"] for example in dataset.examples]
    languages = {example.language for example in dataset.examples}

    assert len(dataset) == 35
    assert set(labels) == {
        "READ_ONLY",
        "MODIFY",
        "SECURITY_SENSITIVE",
        "DESTRUCTIVE",
        "DATA_ACCESS",
        "PRIVILEGED",
        "UNKNOWN",
    }
    assert languages == {"en", "es"}


def test_regex_baseline_runs_through_laya_official_evaluator():
    dataset = Dataset.from_jsonl(str(DATASET))
    report = evaluate(
        RegexBaselineRunner(),
        dataset,
        evaluators=[ChoiceAccuracy()],
    )

    assert report.overall["choice_accuracy"] < 1.0
    assert len(report.cases) == len(dataset)


def test_laya_comparison_runner_contract_without_loading_weights():
    class FakeRouter:
        def predict(self, state, questions, model=None):
            return {
                "answers": {
                    "operation_type": {
                        "type": "choice",
                        "choice": "UNKNOWN",
                        "answer_confidence": 0.5,
                    }
                }
            }

    laya_report, regex_report = evaluate_laya_vs_regex(DATASET, FakeRouter())

    assert laya_report.config["classifier"] == "laya-router"
    assert regex_report.config["classifier"] == "regex"
    assert laya_report.config["dataset_sha256"] == regex_report.config["dataset_sha256"]
    assert "ece" in laya_report.overall