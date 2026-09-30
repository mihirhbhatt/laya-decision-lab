import argparse
import json
from dataclasses import asdict
from pathlib import Path

from laya import Router

from laya_labs.evaluation import evaluate_laya_vs_regex

DEFAULT_DATASET = (
    Path(__file__).resolve().parents[2]
    / "research"
    / "evals"
    / "laya_security_classification.jsonl"
)


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate Laya security classification against a regex baseline."
    )
    parser.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    parser.add_argument("--device", choices=("cpu", "cuda", "mps"))
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    router = Router(device=args.device)
    laya_report, regex_report = evaluate_laya_vs_regex(
        args.dataset,
        laya_router=router,
        batch_size=args.batch_size,
    )

    print(f"Dataset: {args.dataset}")
    print(f"Cases: {len(laya_report.cases)} labeled decisions")
    print(f"Laya choice accuracy: {laya_report.overall['choice_accuracy']:.3f}")
    print(f"Regex baseline accuracy: {regex_report.overall['choice_accuracy']:.3f}")
    if "ece" in laya_report.overall:
        print(f"Laya expected calibration error: {laya_report.overall['ece']:.3f}")
    print("Review language/category slices in the report; this starter set is not a certification.")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(
                {
                    "laya": asdict(laya_report),
                    "regex_baseline": asdict(regex_report),
                },
                indent=2,
                default=str,
            ),
            encoding="utf-8",
        )
        print(f"Report written: {args.output}")


if __name__ == "__main__":
    main()