# Benchmark Plan: stroke-signal-demo

## Hypothesis

reproducao de classificador clinico, measured by accuracy, confusion_matrix.

## Command

```bash
stroke-signal-demo benchmark --n-samples 5000 --seed 42 --output benchmarks/results/baseline.json
```

## Environment

- OS: Linux (Docker container, python:3.12-slim)
- CPU: 1+ cores
- RAM: 256MB+
- GPU: none
- Docker version: any with Dockerfile support
- Date: recorded in result JSON

## Inputs

- fixture: synthetic (src/stroke_signal/fixture.py)
- dataset size: 5000 samples (configurable via --n-samples)
- repetitions: 1 (configurable via --repeats)
- warmup: none (deterministic pipeline)

## Metrics

| Metric | Unit | Source | Why it matters |
|---|---|---|---:|---|
| accuracy | unit | sklearn.metrics.accuracy_score | primary classification quality |
| precision | unit | sklearn.metrics.precision_score | false positive control |
| recall | unit | sklearn.metrics.recall_score | false negative control |
| f1_score | unit | sklearn.metrics.f1_score | balanced harmonic mean |
| tn/fp/fn/tp | count | sklearn.metrics.confusion_matrix | full confusion matrix breakdown |

## Result schema

Output must be JSON and include project, metric, value, unit, timestamp, environment, and command. See `domain.py` BenchmarkResult for the full schema.

## Post angle

#4 stroke-signal-demo: accuracy=0.987 as a reproducible portfolio benchmark.
