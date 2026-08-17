from __future__ import annotations

import argparse
import json
import statistics
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

METRICS = (
    "segmentation_dice",
    "sensitivity",
    "specificity",
    "accuracy",
    "iou",
    "latency_p50_ms",
    "latency_p95_ms",
)


def _load(path: Path) -> dict[str, Any]:
    result = json.loads(path.read_text(encoding="utf-8"))
    if result.get("project") != "stroke-signal-demo":
        raise ValueError(f"{path} belongs to another project")
    if result.get("metric") != "segmentation_dice" or result.get("unit") != "ratio":
        raise ValueError(f"{path} has an incompatible benchmark contract")
    if result.get("failures") != 0 or result.get("repeat") != 1:
        raise ValueError(f"{path} is not one successful independent run")
    if result.get("split", {}).get("overlap_count") != 0:
        raise ValueError(f"{path} contains patient leakage")
    return result


def aggregate(paths: list[Path], output: Path) -> dict[str, Any]:
    if len(paths) < 3:
        raise ValueError("at least three raw benchmark results are required")
    results = [_load(path) for path in paths]
    image_ids = {result["environment"].get("image_id") for result in results}
    if len(image_ids) != 1 or None in image_ids or "not-recorded" in image_ids:
        raise ValueError("all runs must use the same recorded image digest")
    signatures = {
        json.dumps(result["proof"]["benchmark_signature"], sort_keys=True)
        for result in results
    }
    if len(signatures) != 1:
        raise ValueError("raw benchmark signatures differ")
    split_signatures = {
        json.dumps(result["split"], sort_keys=True) for result in results
    }
    if len(split_signatures) != 1:
        raise ValueError("raw patient splits differ")

    aggregate_result = deepcopy(results[0])
    aggregate_result["timestamp"] = (
        datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")  # noqa: UP017
    )
    aggregate_result["repeat"] = len(results)
    aggregate_result["samples"] = [float(result["value"]) for result in results]
    aggregate_result["value"] = statistics.median(aggregate_result["samples"])
    aggregate_result["results"] = [path.name for path in paths]
    aggregate_result["samples_by_metric"] = {}
    for name in METRICS:
        samples = [float(result["metrics"][name]) for result in results]
        aggregate_result["metrics"][name] = statistics.median(samples)
        aggregate_result["samples_by_metric"][name] = samples
    aggregate_result["environment"]["aggregated_runs"] = len(results)
    aggregate_result["proof"]["aggregate"] = "median with every raw sample preserved"
    aggregate_result["proof"]["raw_results"] = [path.name for path in paths]
    aggregate_result["failures"] = sum(int(result["failures"]) for result in results)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(aggregate_result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return aggregate_result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("inputs", nargs="+", type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    aggregate(sorted(args.inputs), args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
