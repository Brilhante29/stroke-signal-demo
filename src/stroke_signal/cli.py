from __future__ import annotations

import argparse
from pathlib import Path

from stroke_signal.benchmark import run_benchmark


def _add_workload_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--patients", type=int, default=30)
    parser.add_argument("--slices-per-patient", type=int, default=4)
    parser.add_argument("--image-size", type=int, default=96)
    parser.add_argument("--seed", type=int, default=2023)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Paper-inspired hemorrhagic-stroke segmentation evaluation"
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    benchmark_parser = subparsers.add_parser("benchmark", help="run the held-out benchmark")
    _add_workload_arguments(benchmark_parser)
    benchmark_parser.add_argument("--output", type=Path)
    demo_parser = subparsers.add_parser(
        "demo", help="run the same protocol without writing JSON"
    )
    _add_workload_arguments(demo_parser)
    args = parser.parse_args(argv)

    result = run_benchmark(
        patient_count=args.patients,
        slices_per_patient=args.slices_per_patient,
        image_size=args.image_size,
        seed=args.seed,
        output_path=getattr(args, "output", None),
    )
    metrics = result.metrics
    print(f"segmentation_dice={result.value:.6f}")
    print(f"sensitivity={metrics['sensitivity']:.6f}")
    print(f"specificity={metrics['specificity']:.6f}")
    print(f"accuracy={metrics['accuracy']:.6f}")
    print(
        "confusion_matrix="
        f"[[{metrics['true_negative']}, {metrics['false_positive']}], "
        f"[{metrics['false_negative']}, {metrics['true_positive']}]]"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
