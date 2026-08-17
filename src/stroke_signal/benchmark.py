from __future__ import annotations

import hashlib
import json
import os
import platform
import time
from datetime import datetime, timezone
from pathlib import Path
from statistics import median

import numpy as np
import scipy

from stroke_signal.domain import BenchmarkResult
from stroke_signal.fixture import fixture_digest, generate_fixture
from stroke_signal.model import (
    confusion_counts,
    samples_for_patients,
    segment_slice,
    select_model,
    split_patients,
)

PAPER_DOI = "10.1109/IJCNN54540.2023.10191320"
METHOD_SCOPE = "paper-inspired synthetic methodology reconstruction"


def _sha256(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture_manifest_path() -> Path:
    relative = Path("data/clinical-fixture-manifest.json")
    candidates = (Path.cwd() / relative, Path(__file__).resolve().parents[2] / relative)
    for candidate in candidates:
        if candidate.is_file():
            return candidate
    raise FileNotFoundError(f"cannot locate {relative}")


def run_benchmark(
    patient_count: int = 30,
    slices_per_patient: int = 4,
    image_size: int = 96,
    seed: int = 2023,
    threshold_offsets: tuple[float, ...] = (-6.0, -3.0, 0.0, 3.0, 6.0),
    output_path: Path | None = None,
) -> BenchmarkResult:
    run_clock = time.perf_counter()
    started_at = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")  # noqa: UP017
    fixture = generate_fixture(patient_count, slices_per_patient, image_size, seed)
    split = split_patients(fixture, seed)
    training = samples_for_patients(fixture, split.train)
    validation = samples_for_patients(fixture, split.validation)
    test = samples_for_patients(fixture, split.test)

    model = select_model(training, validation, threshold_offsets)
    latencies_ms: list[float] = []
    for sample in test:
        start = time.perf_counter()
        segment_slice(sample.image, model)
        latencies_ms.append((time.perf_counter() - start) * 1000)
    metrics = confusion_counts(test, model)
    values = metrics.as_dict()
    values["latency_p50_ms"] = median(latencies_ms)
    values["latency_p95_ms"] = float(np.percentile(latencies_ms, 95))
    values["test_slices"] = len(test)
    values["test_positive_pixels"] = int(sum(sample.mask.sum() for sample in test))

    command = (
        "stroke-signal-demo benchmark"
        f" --patients {patient_count} --slices-per-patient {slices_per_patient}"
        f" --image-size {image_size} --seed {seed}"
    )
    manifest_path = _fixture_manifest_path()
    result = BenchmarkResult(
        schema_version=1,
        project="stroke-signal-demo",
        metric="segmentation_dice",
        value=metrics.dice,
        unit="ratio",
        timestamp=started_at,
        command=command,
        repeat=1,
        measured_iterations=len(test),
        samples=[metrics.dice],
        metrics=values,
        dataset={
            "kind": "deterministic-synthetic-ct-phantom",
            "clinical_use": False,
            "patient_count": patient_count,
            "slices_per_patient": slices_per_patient,
            "image_size": [image_size, image_size],
            "seed": seed,
            "generated_dataset_sha256": fixture_digest(fixture),
            "manifest_sha256": _sha256(manifest_path),
        },
        split={
            "unit": "patient",
            "train_patient_ids": list(split.train),
            "validation_patient_ids": list(split.validation),
            "test_patient_ids": list(split.test),
            "overlap_count": 0,
            "test_used_for_selection": False,
        },
        model={
            "name": "quadrant-seeded-adaptive-region-growth",
            "calibration_threshold": model.calibration_threshold,
            "stopping_threshold": model.stopping_threshold,
            "minimum_component_pixels": model.minimum_component_pixels,
            "artifact_sha256": model.artifact_sha256,
        },
        environment={
            "python": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine() or "unknown",
            "numpy": np.__version__,
            "scipy": scipy.__version__,
            "image_id": os.getenv("IMAGE_ID", "not-recorded"),
            "duration_seconds": time.perf_counter() - run_clock,
        },
        proof={
            "paper_doi": PAPER_DOI,
            "scope": METHOD_SCOPE,
            "published_stroke_metrics": {
                "accuracy": 0.9980,
                "sensitivity": 0.9982,
                "specificity": 0.9981,
                "dice": 0.9325,
            },
            "benchmark_signature": {
                "patient_count": patient_count,
                "slices_per_patient": slices_per_patient,
                "image_size": image_size,
                "test_slices": len(test),
                "seed": seed,
                "threshold_offsets": list(threshold_offsets),
                "generated_dataset_sha256": fixture_digest(fixture),
                "model_artifact_sha256": model.artifact_sha256,
            },
            "limitations": [
                "synthetic CT phantoms are not the private 25-exam clinical dataset",
                "the Detectron2 R50-FPN detector and clinical weights are not reproduced",
                "results do not establish diagnostic or medical-device performance",
            ],
        },
        failures=0,
    )
    if output_path is not None:
        result.to_json(output_path)
    return result


def load_workload(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))
