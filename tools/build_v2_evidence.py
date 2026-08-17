from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import subprocess
import uuid
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

METRIC_CONTRACT = {
    "segmentation_dice": ("ratio", "higher_is_better"),
    "sensitivity": ("ratio", "higher_is_better"),
    "specificity": ("ratio", "higher_is_better"),
    "accuracy": ("ratio", "higher_is_better"),
    "iou": ("ratio", "higher_is_better"),
    "latency_p95_ms": ("milliseconds", "lower_is_better"),
}


def digest(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def git_blob(root: Path, commit: str, path: str) -> bytes:
    return subprocess.run(
        ["git", "-C", str(root), "show", f"{commit}:{path}"],
        check=True,
        capture_output=True,
    ).stdout


def _metric(name: str, values: list[float]) -> dict[str, Any]:
    unit, direction = METRIC_CONTRACT[name]
    return {
        "name": name,
        "value": statistics.median(values),
        "unit": unit,
        "direction": direction,
        "samples": values,
        "failures": 0,
        "summary": {
            "min": min(values),
            "max": max(values),
            "mean": statistics.fmean(values),
            "median": statistics.median(values),
        },
    }


def build(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.root).resolve()
    workload_bytes = git_blob(root, args.source_commit, args.workload_ref)
    workload = json.loads(workload_bytes)
    raw_paths = sorted(Path(args.results_directory).glob("run-*.json"))
    runs = [json.loads(path.read_text(encoding="utf-8")) for path in raw_paths]
    if len(runs) != workload["repetitions"] or len(runs) != args.repetitions:
        raise ValueError("raw run count differs from source-locked workload")
    if any(run.get("failures") != 0 or run.get("repeat") != 1 for run in runs):
        raise ValueError("raw benchmark runs must be independent and failure-free")
    signatures = {
        json.dumps(run["proof"]["benchmark_signature"], sort_keys=True) for run in runs
    }
    if len(signatures) != 1:
        raise ValueError("raw benchmark signatures differ")
    signature = json.loads(next(iter(signatures)))
    for name in ("patient_count", "slices_per_patient", "image_size", "test_slices", "seed"):
        if signature[name] != workload[name]:
            raise ValueError(f"raw benchmark {name} differs from workload")
    image_ids = {run["environment"].get("image_id") for run in runs}
    if image_ids != {args.image_digest}:
        raise ValueError("raw runs do not identify the immutable benchmark image")

    metrics = [
        _metric(name, [float(run["metrics"][name]) for run in runs])
        for name in METRIC_CONTRACT
    ]
    first = runs[0]
    result = {
        "schema_version": 2,
        "run_id": str(uuid.uuid4()),
        "project": "stroke-signal-demo",
        "benchmark_id": workload["benchmark_id"],
        "workload": {
            "version": workload["workload_version"],
            "fixture_digest": digest(
                git_blob(root, args.source_commit, args.fixture_manifest_ref)
            ),
            "config_digest": digest(workload_bytes),
            "warmup_iterations": workload["warmup_iterations"],
            "measured_iterations": workload["test_slices"],
            "concurrency": workload["concurrency"],
        },
        "metrics": metrics,
        "execution": {
            "command": args.command,
            "started_at": min(run["timestamp"] for run in runs),
            "duration_seconds": sum(
                float(run["environment"]["duration_seconds"]) for run in runs
            ),
            "exit_code": 0,
            "repeat": len(runs),
        },
        "environment": {
            "runtime": f"python-{first['environment']['python']}",
            "architecture": first["environment"]["machine"],
            "hardware_class": args.hardware_class,
            "container_platform": first["environment"]["platform"],
            "numpy": first["environment"]["numpy"],
            "scipy": first["environment"]["scipy"],
            "generated_dataset_sha256": first["dataset"]["generated_dataset_sha256"],
            "model_artifact_sha256": first["model"]["artifact_sha256"],
            "split_unit": "patient",
            "test_used_for_selection": False,
        },
        "provenance": {
            "source_commit": args.source_commit,
            "clean_tree": True,
            "image_ref": args.image_ref,
            "image_digest": args.image_digest,
            "dependency_lock_digest": digest(
                git_blob(root, args.source_commit, args.lock_ref)
            ),
            "producer": args.producer,
            "artifact_digest": args.artifact_digest,
        },
        "comparability_key": workload["comparability_key"],
    }
    schema = json.loads(
        (root / ".portfolio/contracts/benchmark-result-v2.schema.json").read_text(
            encoding="utf-8"
        )
    )
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(result)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True)
    parser.add_argument("--results-directory", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--image-ref", required=True)
    parser.add_argument("--image-digest", required=True)
    parser.add_argument("--artifact-digest", required=True)
    parser.add_argument("--hardware-class", required=True)
    parser.add_argument("--repetitions", type=int, required=True)
    parser.add_argument(
        "--producer",
        choices=("local", "github-actions", "other-ci"),
        required=True,
    )
    parser.add_argument("--command", required=True)
    parser.add_argument("--workload-ref", default="benchmarks/workload.json")
    parser.add_argument("--fixture-manifest-ref", default="data/clinical-fixture-manifest.json")
    parser.add_argument("--lock-ref", default="constraints.lock")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(build(args), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
