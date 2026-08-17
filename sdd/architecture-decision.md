# Architecture Decision: Evaluation Pipeline

## Status

Accepted.

## Decision

Use a single-process pipeline with explicit scientific boundaries:

```text
fixture -> patient split -> train calibration -> validation selection
        -> untouched test segmentation -> metrics -> evidence
```

## Why

The problem is ordered, deterministic evaluation with high auditability and no infrastructure integration. Pipeline architecture keeps data lineage visible. MVC has no UI state, MVVM has no view model, hexagonal architecture has no real external adapter, and microservices have no independent deployment boundary.

## Dependency Direction

- `domain.py` contains immutable values and metric formulas.
- `fixture.py` contains synthetic image generation and digest identity.
- `model.py` contains split, calibration, selection, and segmentation policy.
- `benchmark.py` composes the use case and emits evidence.
- `cli.py` is the outer transport.

No inner module imports CLI, Docker, HTTP, database, messaging, orchestration, cloud, or another repository.

## Principles

- SRP: generation, selection, segmentation, metrics, orchestration, and transport are separate.
- OCP: new threshold candidates or fixture versions can be added without changing metric formulas.
- ISP: functions receive only arrays, samples, patient IDs, or immutable model values they need.
- DIP: no infrastructure dependency exists yet; inventing a port would add indirection without substitution value.
- LSP: not applicable because the design intentionally has no subtype hierarchy.
- KISS/YAGNI: one CPU method and one CLI prove the bounded claim.

## Consequences

The project is easy to run and audit, but it cannot claim the paper's detector, dataset, or clinical generalization. A future authorized clinical-data adapter must preserve patient identity and the same evaluation contract without changing domain metric policy.
