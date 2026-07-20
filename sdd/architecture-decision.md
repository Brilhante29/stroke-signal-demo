# Architecture Decision

## Status

Accepted

## Context

Project: `4 - stroke-signal-demo`
Claim: reproducao de classificador clinico
Benchmark: accuracy, confusion_matrix

Problem forces:

- Domain complexity: low
- Integration pressure: low
- UI state complexity: none
- Data/ML reproducibility: high
- Auditability/event history: medium
- Throughput/async pressure: low
- Independent deployability need: low

## Decision

Chosen architecture: `pipeline`

Reason:

A three-stage pipeline (fixture generation -> model training/evaluation -> benchmark output) maps directly to the problem. Data flows in one direction with no branching, state machine, or event loop. The CLI wraps all three stages and provides `demo` and `benchmark` subcommands.

Dependency rule:

fixture depends only on numpy/pandas; model depends on scikit-learn and fixture output; benchmark orchestrates both; CLI depends on all three inward.

## Rejected Alternatives

| Alternative | Why rejected |
|---|---|
| hexagonal | No infrastructure boundary worth isolating; no ports/adapters needed without cloud, database, or transport |
| microservices | Single-process pipeline has no deploy boundary; splitting adds distributed cost without benefit |

## Folder Layout

```
src/
  stroke_signal/
    __init__.py
    __main__.py
    cli.py
    domain.py
    fixture.py
    model.py
    benchmark.py
tests/
  test_domain.py
  test_model.py
benchmarks/
  results/
    baseline.json
```

## Testing Strategy

- Unit tests: domain types (BenchmarkResult construction and serialization)
- Integration tests: model train/evaluate with synthetic data; deterministic repeatability
- Benchmark: full pipeline via CLI or Docker, outputs JSON to benchmarks/results/

## Consequences

Positive:

- Simple three-stage pipeline is easy to understand and modify.
- Deterministic synthetic data ensures reproducible benchmarks across environments.
- No external dependencies for default path.

Tradeoffs:

- Synthetic data may not reflect real-world feature distributions; the claim is about classifier reproducibility, not clinical accuracy.
- RandomForest with default params may overfit to synthetic distribution; benchmark transparency addresses this via seed and environment recording.
