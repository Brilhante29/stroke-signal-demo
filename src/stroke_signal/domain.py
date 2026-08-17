from __future__ import annotations

import dataclasses
import json
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True)
class PatientSplit:
    train: tuple[str, ...]
    validation: tuple[str, ...]
    test: tuple[str, ...]

    def assert_isolated(self) -> None:
        groups = (set(self.train), set(self.validation), set(self.test))
        if any(groups[left] & groups[right] for left, right in ((0, 1), (0, 2), (1, 2))):
            raise ValueError("patient identifiers overlap across splits")

    @property
    def patient_count(self) -> int:
        self.assert_isolated()
        return len(self.train) + len(self.validation) + len(self.test)


@dataclasses.dataclass(frozen=True)
class PixelMetrics:
    true_negative: int
    false_positive: int
    false_negative: int
    true_positive: int

    def __post_init__(self) -> None:
        if min(dataclasses.astuple(self)) < 0:
            raise ValueError("confusion counts cannot be negative")

    @property
    def total(self) -> int:
        return sum(dataclasses.astuple(self))

    @staticmethod
    def _ratio(numerator: int, denominator: int) -> float:
        return float(numerator / denominator) if denominator else 0.0

    @property
    def accuracy(self) -> float:
        return self._ratio(self.true_positive + self.true_negative, self.total)

    @property
    def sensitivity(self) -> float:
        return self._ratio(self.true_positive, self.true_positive + self.false_negative)

    @property
    def specificity(self) -> float:
        return self._ratio(self.true_negative, self.true_negative + self.false_positive)

    @property
    def dice(self) -> float:
        return self._ratio(
            2 * self.true_positive,
            2 * self.true_positive + self.false_positive + self.false_negative,
        )

    @property
    def iou(self) -> float:
        return self._ratio(
            self.true_positive,
            self.true_positive + self.false_positive + self.false_negative,
        )

    def as_dict(self) -> dict[str, float | int]:
        return {
            "accuracy": self.accuracy,
            "sensitivity": self.sensitivity,
            "specificity": self.specificity,
            "segmentation_dice": self.dice,
            "iou": self.iou,
            "true_negative": self.true_negative,
            "false_positive": self.false_positive,
            "false_negative": self.false_negative,
            "true_positive": self.true_positive,
        }


@dataclasses.dataclass(frozen=True)
class BenchmarkResult:
    schema_version: int
    project: str
    metric: str
    value: float
    unit: str
    timestamp: str
    command: str
    repeat: int
    measured_iterations: int
    samples: list[float]
    metrics: dict[str, float | int]
    dataset: dict[str, Any]
    split: dict[str, Any]
    model: dict[str, Any]
    environment: dict[str, Any]
    proof: dict[str, Any]
    failures: int

    def to_json(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(dataclasses.asdict(self), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
            newline="\n",
        )
