# Agent Handoff

Project: `4 - stroke-signal-demo`

## Principal Agent Summary

- Objective: Reproduzir classificador clinico de AVC com dados sinteticos deterministicos.
- Portfolio program: mlops-data-platform
- Public proof claim: reproducao de classificador clinico
- Primary benchmark: accuracy
- Default runnable path: `docker run --rm stroke-signal-demo`

## Subagent Decisions

| Role | Decision | Evidence Path | Status |
|---|---|---|---|
| `program-planner` | mlops-data-platform | `project.yaml`, `sdd/spec.md` | done |
| `architecture-selector` | pipeline | `sdd/architecture-decision.md` | done |
| `engineering-principles-reviewer` | SOLID + KISS/YAGNI | `project.yaml`, `sdd/technical-decision.md` | done |
| `stack-decision-agent` | python, scikit-learn, pandas | `project.yaml`, `sdd/technical-decision.md` | done |
| `api-style-agent` | CLI (argparse) | CLI contract in README | done |
| `cloud-local-first-agent` | none | Docker-only runtime | done |
| `messaging-agent` | none | `sdd/technical-decision.md` | done |
| `language-profile-agent` | python-ml | repo layout, tests, tooling | done |
| `benchmark-harness-agent` | accuracy benchmark | `sdd/benchmark-plan.md`, `benchmarks/results/baseline.json` | done |
| `design-system-agent` | README with benchmark table | `README.md` | done |
| `security-reuse-reviewer` | no secrets, no network | `REFERENCES.md`, release checklist | done |
| `release-ci-publisher` | validation and CI | CI workflow, validation | done |

## Local-First Runtime

- Docker command: `docker run --rm stroke-signal-demo`
- Local services: none
- Kumo services, if any: none
- Real cloud adapter target, if any: none
- Config switch: none
- Default path requires paid secret: no

## Architecture Boundaries

- Domain boundaries: stroke_signal/domain.py (pure dataclasses)
- Use-case boundaries: fixture -> model -> benchmark
- Ports: function signatures (generate_dataset, train_and_evaluate, run_benchmark)
- Adapters: none (no infrastructure boundaries)
- Dependency direction rule: CLI imports benchmark/model/fixture; benchmark imports model/fixture; model imports fixture

## Benchmark Handoff

- Metric: accuracy
- Unit: unit (0-1 scale)
- Higher or lower is better: higher
- Command: `stroke-signal-demo benchmark --n-samples 5000 --seed 42 --output benchmarks/results/baseline.json`
- Result path: `benchmarks/results/baseline.json`
- Dataset or fixture: synthetic (src/stroke_signal/fixture.py)

## Open Risks

- None

## Publication Gates

- [x] Docker path works
- [x] benchmark result exists
- [x] README starts with number, claim, and benchmark
- [x] references are documented
- [x] no secret in files or git remote
- [x] validation passes
