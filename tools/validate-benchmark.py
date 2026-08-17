from __future__ import annotations

import json
import math
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
RESULT = ROOT / "benchmarks/results/baseline.json"
SCHEMA = ROOT / "contracts/medical-evaluation-report-v1.schema.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> None:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(result)
    require(result["repeat"] >= 3, "canonical baseline requires at least three runs")
    require(result["failures"] == 0, "canonical baseline contains failures")
    require(
        result["dataset"]["clinical_use"] is False,
        "synthetic data cannot claim clinical use",
    )
    require(result["split"]["overlap_count"] == 0, "patient leakage detected")
    require(
        result["split"]["test_used_for_selection"] is False,
        "test split selected the model",
    )
    groups = [set(result["split"][name]) for name in (
        "train_patient_ids", "validation_patient_ids", "test_patient_ids"
    )]
    require(
        not any(groups[a] & groups[b] for a, b in ((0, 1), (0, 2), (1, 2))),
        "split IDs overlap",
    )

    metrics = result["metrics"]
    tn, fp, fn, tp = (int(metrics[name]) for name in (
        "true_negative", "false_positive", "false_negative", "true_positive"
    ))
    expected_pixels = result["measured_iterations"] * math.prod(result["dataset"]["image_size"])
    require(tn + fp + fn + tp == expected_pixels, "confusion matrix does not cover test pixels")
    require(math.isclose(metrics["sensitivity"], tp / (tp + fn)), "invalid sensitivity")
    require(math.isclose(metrics["specificity"], tn / (tn + fp)), "invalid specificity")
    require(math.isclose(metrics["accuracy"], (tp + tn) / expected_pixels), "invalid accuracy")
    require(
        math.isclose(metrics["segmentation_dice"], 2 * tp / (2 * tp + fp + fn)),
        "invalid Dice",
    )
    require(result["value"] == metrics["segmentation_dice"], "primary metric mismatch")
    require(
        result["proof"]["paper_doi"] == "10.1109/IJCNN54540.2023.10191320",
        "paper DOI mismatch",
    )
    require(
        "synthetic" in result["proof"]["scope"],
        "scope must state synthetic reconstruction",
    )
    require(len(result["proof"]["limitations"]) >= 3, "medical limitations are incomplete")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for expected in (
        f"{result['value']:.4f}",
        f"{metrics['sensitivity']:.4f}",
        f"{metrics['specificity']:.4f}",
        str(metrics["true_positive"]),
    ):
        require(expected in readme, f"README is missing benchmark value {expected}")
    require(
        "not a clinical reproduction" in readme.lower(),
        "README must bound the public claim",
    )
    print("benchmark_contract=passed")


if __name__ == "__main__":
    main()
