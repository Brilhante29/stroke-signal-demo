from __future__ import annotations

import argparse
import time
from pathlib import Path

from stroke_signal.domain import BenchmarkResult
from stroke_signal.fixture import generate_dataset
from stroke_signal.model import train_and_evaluate


def run_benchmark(
    n_samples: int = 5000,
    seed: int = 42,
    output_path: Path | None = None,
    repeats: int = 1,
) -> BenchmarkResult:
    times: list[float] = []
    final_result: BenchmarkResult | None = None

    for i in range(repeats):
        df = generate_dataset(n_samples=n_samples, seed=seed + i)
        start = time.perf_counter()
        metrics = train_and_evaluate(df, seed=seed + i)
        elapsed = time.perf_counter() - start
        times.append(elapsed)

        cm = metrics["confusion_matrix"]
        final_result = BenchmarkResult.from_metrics(
            accuracy=metrics["accuracy"],
            confusion_matrix=cm,
            precision=metrics["precision"],
            recall=metrics["recall"],
            f1=metrics["f1"],
            n_samples=n_samples,
            seed=seed + i,
            command=(
                f"stroke-signal-demo benchmark"
                f" --n-samples {n_samples}"
                f" --seed {seed + i}"
                f" --output {output_path or 'stdout'}"
            ),
            output_path=output_path or Path("benchmarks/results/default.json"),
        )
        final_result.environment["repeat"] = i + 1
        final_result.environment["elapsed_seconds"] = round(elapsed, 4)
        final_result.environment["repeats"] = repeats
        final_result.metrics["elapsed_seconds"] = round(elapsed, 4)

    if output_path:
        assert final_result is not None
        output_path.parent.mkdir(parents=True, exist_ok=True)
        final_result.to_json(output_path)

    return final_result


def main() -> int:
    parser = argparse.ArgumentParser(
        description="stroke-signal-demo benchmark harness"
    )
    parser.add_argument(
        "--n-samples",
        type=int,
        default=5000,
        help="number of synthetic samples",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="random seed",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="output JSON path",
    )
    parser.add_argument(
        "--repeats",
        type=int,
        default=1,
        help="number of benchmark repeats",
    )
    args = parser.parse_args()

    result = run_benchmark(
        n_samples=args.n_samples,
        seed=args.seed,
        output_path=args.output,
        repeats=args.repeats,
    )

    print(f"accuracy={result.value:.6f}")
    print(f"metrics={result.metrics}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
