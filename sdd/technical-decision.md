# Technical Decision

## Status

Accepted.

## Stack

- Python 3.12.13 for the scientific CLI.
- NumPy 2.5.1 for deterministic arrays and fixtures.
- SciPy 1.18.0 for reviewed morphology and connected-component operations.
- Jsonschema 4.26.0 for V1 and V2 evidence validation.
- Pytest, coverage, and Ruff for executable quality gates.
- Multi-stage, digest-pinned, non-root Docker runtime.

## Method Boundary

The paper uses Detectron2 R50-FPN automatic detection followed by Divisible Cell-Segmentation on a private clinical dataset. This repository reconstructs only the inspectable concepts needed for an offline methodological demonstration: recursive quadrant seed search and threshold-bounded region growth.

The old RandomForest risk classifier was rejected because it solved tabular risk prediction rather than CT lesion segmentation. Full Detectron2 was rejected because neither the paper's training data nor weights are distributed here; adding it would create a large image without producing faithful evidence.

## Protocol

1. Generate versioned synthetic patients and slices.
2. Split by patient, never by slice.
3. Fit intensity calibration on training labels only.
4. Select the stopping threshold on validation patients only.
5. Evaluate once on test patients and derive every metric from one confusion matrix.
6. Bind three runs to exact source, image, wheel, lock, fixture, split, and model digests.

## Operational Decisions

- CLI, not HTTP or GraphQL: output is an evaluation artifact.
- No messaging: there is no asynchronous delivery requirement.
- No database: all workload state is bounded and immutable.
- No Kumo/cloud: no AWS behavior participates in the proof.
- No MLflow/Airflow: #21 already owns lifecycle orchestration; duplicating it would weaken macro boundaries.
