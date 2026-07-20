from __future__ import annotations

import argparse
import sys
from pathlib import Path

from stroke_signal.benchmark import run_benchmark
from stroke_signal.fixture import generate_dataset
from stroke_signal.model import train_and_evaluate


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="stroke-signal-demo: reproducible stroke classifier"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    benchmark_parser = sub.add_parser("benchmark", help="run benchmark")
    benchmark_parser.add_argument(
        "--n-samples", type=int, default=5000
    )
    benchmark_parser.add_argument("--seed", type=int, default=42)
    benchmark_parser.add_argument("--output", type=Path, default=None)
    benchmark_parser.add_argument("--repeats", type=int, default=1)

    demo_parser = sub.add_parser("demo", help="run quick demo")
    demo_parser.add_argument("--n-samples", type=int, default=1000)
    demo_parser.add_argument("--seed", type=int, default=42)

    args = parser.parse_args(argv)

    if args.command == "benchmark":
        result = run_benchmark(
            n_samples=args.n_samples,
            seed=args.seed,
            output_path=args.output,
            repeats=args.repeats,
        )
        print(f"accuracy={result.value:.6f}")
        return 0

    if args.command == "demo":
        df = generate_dataset(n_samples=args.n_samples, seed=args.seed)
        metrics = train_and_evaluate(df, seed=args.seed)
        print(f"samples={len(df)}")
        print(f"accuracy={metrics['accuracy']:.6f}")
        print(f"confusion_matrix={metrics['confusion_matrix']}")
        print(f"precision={metrics['precision']:.6f}")
        print(f"recall={metrics['recall']:.6f}")
        print(f"f1={metrics['f1']:.6f}")
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
