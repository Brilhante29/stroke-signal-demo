# Technical Decision

## Status

Accepted

## Decision Type

stack, library, runtime

## Context

Project: `4 - stroke-signal-demo`
Problem: Reproduzir classificador clinico de AVC com dados sinteticos deterministicos
Portfolio program: mlops-data-platform
Public signal: reproducao de benchmark ML em Docker
Benchmark: accuracy, confusion_matrix

## Selected Option

Selected: scikit-learn RandomForest + synthetic fixture

Reason:

Tabular classification com ~5% de taxa positiva, 7 features numericas/binarias e benchmark de accuracy e matriz de confusao. RandomForest oferece bom desempenho sem GPU, convergencia deterministica com seed fixa, e `class_weight="balanced"` para dados desbalanceados.

## Decision Brain Fields

- Stack profile: python-ml
- API style: cli
- Messaging: none
- Cloud mode: none
- Database/runtime: none (synthetic data in memory)
- Library policy: scikit-learn para classificacao e metricas; pandas para geracao de fixture; argparse para CLI

## Engineering Principles

Coupling boundary:

Domain types (BenchmarkResult) depend only on standard library. Model imports scikit-learn and pandas. CLI imports argparse.

SOLID application:

- SRP: fixture generation, model training, and benchmark output are separate modules.
- OCP: new classifiers can be added without modifying existing evaluation code.
- LSP: fixture output (DataFrame) is substitutable for any compatible dataset shape.
- ISP: CLI depends on small function signatures (run_benchmark, generate_dataset, train_and_evaluate).
- DIP: benchmark orchestrates high-level functions, not class hierarchies.

Simplicity:

- KISS: one classifier, one fixture, one JSON output.
- YAGNI: no model serving, no experiment tracking, no hyperparameter optimization.
- DRY: evaluation metrics computed once by scikit-learn, recorded by benchmark module.

Testability evidence:

- Domain types test BenchmarkResult construction and JSON roundtrip.
- Model tests verify deterministic repeatability and accuracy above baseline.
- No network, database, or cloud dependency required for any test.

## Rejected Options

| Option | Why rejected |
|---|---|
| PyTorch classifier | Overkill for tabular data; GPU not available in default Docker path; scikit-learn is simpler and equally effective |
| Real medical dataset | Introduces network dependency and licensing risk; synthetic fixture is deterministic and reproducible |
| FastAPI serving endpoint | No UI or API requirement in the claim; CLI is sufficient for benchmark execution |

## API Contract

Contract artifact: CLI argparse (`demo`, `benchmark` subcommands)

## Cloud Local-First

Local provider: none
Real provider target: none
Config switch: none

## Benchmark Impact

Expected impact: accuracy >= 0.95 with 5000 synthetic samples, seed 42

Validation command:

```powershell
stroke-signal-demo benchmark --n-samples 5000 --seed 42 --output benchmarks/results/validation.json
```

## Operational Cost

- Docker services added: none
- Local demo complexity: low
- Failure case required: no

## Follow-up

- N/A
