# Spec: stroke-signal-demo

## Intent

Project #4 must demonstrate a leakage-safe hemorrhagic-stroke CT segmentation evaluation inspired by Divisible Cell-Segmentation. It must not claim to reproduce private clinical data, Detectron2 weights, or diagnostic performance.

## In Scope

- Deterministic synthetic CT phantoms with patient and slice identity.
- Patient-level train, validation, and test isolation.
- Train-only calibration and validation-only threshold selection.
- Quadrant seed initialization and threshold-bounded connected-region growth.
- Untouched test Dice, sensitivity, specificity, accuracy, IoU, confusion matrix, and latency.
- Source, image, wheel, lock, fixture, split, and model identity in V2 evidence.
- Offline non-root Docker execution.

## Out Of Scope

- Clinical diagnosis, safety, generalization, fairness, calibration, or medical-device claims.
- Redistribution of the paper's 25 examinations or any other patient data.
- Full Detectron2 R50-FPN training without authorized data and paper weights.
- API serving, UI, database, broker, orchestration, Kumo, or real cloud.

## Acceptance

- `docker run --rm --network none stroke-signal-demo` completes without secrets.
- No patient ID appears in more than one split.
- Test IDs do not participate in calibration or threshold selection.
- Confusion counts cover every test pixel and exactly derive all reported metrics.
- Three raw runs from one immutable image produce a source-locked V2 artifact.
- README opens with #4, measured synthetic numbers, paper attribution, and limitations.
