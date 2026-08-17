# Benchmark Proof

- Primary metric: segmentation Dice.
- Required context: sensitivity, specificity, accuracy, IoU, TN, FP, FN, TP, p95 latency.
- Fixture: deterministic synthetic CT phantoms, explicitly non-clinical.
- Split: patient-level 18 / 6 / 6.
- Repetitions: three from one immutable image.
- V1 path: `benchmarks/results/baseline.json`.
- V2 path: `benchmarks/publication/stroke-signal-v2.json`.
