# Benchmark Plan

## Hypothesis

The repository can execute a deterministic, patient-isolated segmentation protocol and preserve enough evidence to detect leakage, metric inconsistency, workload drift, model drift, or artifact substitution.

## Workload

- 30 synthetic patients and 4 slices per patient.
- 18 train, 6 validation, and 6 untouched test patients.
- 96 x 96 pixels, seed 2023, CPU only.
- Five validation threshold candidates around a train-derived calibration.
- Three complete runs from one immutable Docker image.

## Metrics

| Metric | Unit | Direction | Purpose |
|---|---|---|---|
| segmentation Dice | ratio | higher | overlap quality without background dominance |
| sensitivity | ratio | higher | false-negative control |
| specificity | ratio | higher | false-positive control |
| accuracy | ratio | higher | required context, interpreted with class imbalance |
| IoU | ratio | higher | overlap comparison |
| p95 slice latency | ms | lower | CPU execution cost |
| TN / FP / FN / TP | pixels | n/a | auditable confusion matrix |

## Command

```powershell
./tools/benchmark.ps1
```

Raw runs are temporary. The committed outputs are `benchmarks/results/baseline.json` and `benchmarks/publication/stroke-signal-v2.json`.

## Interpretation

Synthetic quality metrics are regression evidence for this generated workload. They are not comparable to clinical performance. Published paper metrics remain attribution-only and are never merged with repository measurements.
