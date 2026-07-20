from __future__ import annotations

import json
from pathlib import Path

from stroke_signal.domain import BenchmarkResult


class TestBenchmarkResult:
    def test_from_metrics_builds_valid_result(self):
        result = BenchmarkResult.from_metrics(
            accuracy=0.85,
            confusion_matrix=[[100, 10], [15, 75]],
            precision=0.88,
            recall=0.83,
            f1=0.85,
            n_samples=5000,
            seed=42,
            command="stroke-signal-demo benchmark --n-samples 5000",
            output_path=Path("benchmarks/results/test.json"),
        )
        assert result.project == "4-stroke-signal-demo"
        assert result.metric == "accuracy"
        assert result.value == 0.85
        assert result.metrics["accuracy"] == 0.85
        assert result.metrics["tn"] == 100
        assert result.metrics["tp"] == 75
        assert result.failures == 0

    def test_to_json_roundtrip(self, tmp_path: Path):
        path = tmp_path / "result.json"
        result = BenchmarkResult.from_metrics(
            accuracy=0.9,
            confusion_matrix=[[50, 5], [8, 37]],
            precision=0.9,
            recall=0.9,
            f1=0.9,
            n_samples=1000,
            seed=7,
            command="test",
            output_path=path,
        )
        result.to_json(path)
        assert path.exists()
        data = json.loads(path.read_text())
        assert data["project"] == "4-stroke-signal-demo"
        assert data["value"] == 0.9
