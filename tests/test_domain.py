from __future__ import annotations

import json
from pathlib import Path

import pytest

from stroke_signal.domain import BenchmarkResult, PatientSplit, PixelMetrics


def test_patient_split_rejects_overlap() -> None:
    split = PatientSplit(("a",), ("b",), ("a",))
    with pytest.raises(ValueError, match="overlap"):
        split.assert_isolated()


def test_patient_split_counts_isolated_patients() -> None:
    split = PatientSplit(("a", "b"), ("c",), ("d",))
    assert split.patient_count == 4


def test_pixel_metrics_compute_clinical_values() -> None:
    metrics = PixelMetrics(80, 20, 10, 90)
    assert metrics.total == 200
    assert metrics.accuracy == 0.85
    assert metrics.sensitivity == 0.9
    assert metrics.specificity == 0.8
    assert metrics.dice == 0.8571428571428571
    assert metrics.iou == 0.75
    assert metrics.as_dict()["true_positive"] == 90


def test_pixel_metrics_handle_empty_denominator_and_invalid_counts() -> None:
    assert PixelMetrics(0, 0, 0, 0).accuracy == 0.0
    with pytest.raises(ValueError, match="negative"):
        PixelMetrics(-1, 0, 0, 0)


def test_benchmark_result_serializes(tmp_path: Path) -> None:
    output = tmp_path / "result.json"
    result = BenchmarkResult(
        1,
        "stroke-signal-demo",
        "segmentation_dice",
        0.8,
        "ratio",
        "2026-01-01T00:00:00Z",
        "benchmark",
        1,
        2,
        [0.8],
        {},
        {},
        {},
        {},
        {},
        {},
        0,
    )
    result.to_json(output)
    assert json.loads(output.read_text(encoding="utf-8"))["value"] == 0.8
