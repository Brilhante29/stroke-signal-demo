# Agent Handoff

## Current Objective

Publish #4 as the sixth and final repository in `mlops-data-platform`, then promote the verified medical evaluation contract into `portfolio-reuse-kit`.

## Decisions Already Made

- The cited work is Divisible Cell-Segmentation, DOI `10.1109/IJCNN54540.2023.10191320`.
- The old tabular RandomForest implementation was a claim mismatch and was replaced.
- The repository is a paper-inspired synthetic methodology reconstruction, not a clinical reproduction.
- Architecture is a single evaluation pipeline; API is CLI; messaging, database, cloud, and Kumo are not applicable.
- Test selection is forbidden: calibration uses train patients, threshold uses validation patients, metrics use test patients.

## Evidence Paths

- Public claim and numbers: `README.md`.
- Workload: `benchmarks/workload.json`.
- Raw aggregate: `benchmarks/results/baseline.json`.
- Publication proof: `benchmarks/publication/stroke-signal-v2.json`.
- Medical contract: `contracts/medical-evaluation-report-v1.schema.json`.
- Source decisions: `sdd/` and `openspec/artifacts/`.

## Remaining Publication Steps

1. Commit the canonical V1/V2 evidence and publication metadata.
2. Push `main` and confirm an exact-head GitHub Actions run.
3. Record that run in this checklist and in the reuse kit.
4. Promote the generic medical contract to the reuse kit and close the macro at 6/6.

## Verified Local State

- Source commit: `ed1c8aee181b195d4aceeba9d08221486ee6b6ba`.
- Three-run synthetic Dice: `0.9424706943192065`; failures: `0`.
- Docker image: `sha256:0127593111e44059f0bc358f3eb629ab563ff550faac2765375def485b39f89d` (`438442627` bytes).
- Test suite: `21` passing with more than `97%` line coverage.

## Open Risk

Clinical generalization remains untested because the paper dataset is private and the public PhysioNet alternative requires a data-use agreement. Do not remove this limitation or compare synthetic metrics directly with patient results.
