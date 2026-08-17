# Reuse Improvement Review

Project: `4 - stroke-signal-demo`

## Findings

| Finding | Classification | Kit area | Resolution |
|---|---|---|---|
| Synthetic labels directly controlled the features measured by the old classifier | `patch_now` | medical AI skill | Skill now requires rejecting circular synthetic quality claims; README and benchmark bound the current result |
| Medical repositories need patient split, threshold, confusion, model, and dataset identity | `patch_now` | contracts | `medical-evaluation-report-v1` implemented locally and queued for promotion after this first verified consumer |
| Three-run source/image/wheel evidence applies across scientific projects | `reuse_existing` | benchmark harness | Reused benchmark-result-v2 and publish-benchmark-evidence skill |
| Detectron2, FastAPI, MLflow, broker, or cloud would not participate in this proof | `reject` | stack decision | Kept out under KISS/YAGNI |

## Reuse Delta

The project exposed one generic contract candidate: a medical evaluation report must bind patient-isolated split identity, threshold policy, model artifact, dataset provenance, clinical-use flag, and confusion matrix. The implementation remains local until its publication validation passes; then the schema and guidance can be promoted to `portfolio-reuse-kit` without coupling other repositories to this source tree.

## Final gate

- [x] Reusable improvements were patched or recorded.
- [x] Project-specific implementation was not moved into the kit.
- [x] Validation reflects patient isolation, medical scope, confusion consistency, and V2 evidence.
