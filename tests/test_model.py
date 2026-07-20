from __future__ import annotations

from stroke_signal.fixture import generate_dataset
from stroke_signal.model import train_and_evaluate


class TestTrainAndEvaluate:
    def test_returns_expected_keys(self):
        df = generate_dataset(n_samples=500, seed=42)
        result = train_and_evaluate(df, seed=42)
        assert "accuracy" in result
        assert "confusion_matrix" in result
        assert "precision" in result
        assert "recall" in result
        assert "f1" in result

    def test_accuracy_above_baseline(self):
        df = generate_dataset(n_samples=2000, seed=42)
        result = train_and_evaluate(df, seed=42)
        assert result["accuracy"] > 0.5

    def test_deterministic_repeatability(self):
        df = generate_dataset(n_samples=1000, seed=99)
        r1 = train_and_evaluate(df, seed=99)
        r2 = train_and_evaluate(df, seed=99)
        assert r1["accuracy"] == r2["accuracy"]
        assert r1["confusion_matrix"] == r2["confusion_matrix"]
