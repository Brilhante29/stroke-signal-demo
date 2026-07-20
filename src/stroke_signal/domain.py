from __future__ import annotations

import dataclasses
import json
import platform
import time
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class BenchmarkResult:
    project: str
    metric: str
    value: float
    unit: str
    timestamp: str
    command: str
    environment: dict[str, Any]
    metrics: dict[str, float]
    proof: dict[str, Any]
    failures: int

    def to_json(self, path: Path) -> None:
        path.write_text(
            json.dumps(dataclasses.asdict(self), indent=2, default=str)
        )

    @staticmethod
    def from_metrics(
        accuracy: float,
        confusion_matrix: list[list[int]],
        precision: float,
        recall: float,
        f1: float,
        n_samples: int,
        seed: int,
        command: str,
        output_path: Path,
    ) -> BenchmarkResult:
        return BenchmarkResult(
            project="4-stroke-signal-demo",
            metric="accuracy",
            value=accuracy,
            unit="unit",
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            command=command,
            environment={
                "python_version": platform.python_version(),
                "platform": platform.platform(),
                "seed": seed,
                "n_samples": n_samples,
                "classifier": "random-forest",
                "n_estimators": 100,
                "test_split": 0.2,
            },
            metrics={
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "tn": confusion_matrix[0][0],
                "fp": confusion_matrix[0][1],
                "fn": confusion_matrix[1][0],
                "tp": confusion_matrix[1][1],
            },
            proof={
                "fixture": "synthetic",
                "fixture_generator": "stroke_signal.fixture.generate_dataset",
                "classifier": "sklearn.ensemble.RandomForestClassifier",
            },
            failures=0,
        )
