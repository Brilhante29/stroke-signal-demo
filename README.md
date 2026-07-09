# #4 stroke-signal-demo

**Status:** scaffold

**Proves:** reproducao de classificador clinico.

**Benchmark target:** accuracy, confusion_matrix.

**Stack:** python, pandas, scikit-learn, matplotlib, docker.

## Next milestone

Implement the smallest Docker-runnable version and produce the first JSON benchmark under enchmarks/results/.

## Run

`ash
docker build -t stroke-signal-demo .
docker run --rm stroke-signal-demo
`

## Benchmark

`ash
docker run --rm stroke-signal-demo benchmark
`

| Metric | Value | Unit |
|---|---:|---|
| accuracy, confusion_matrix | pending | pending |

## Architecture

Defined in sdd/spec.md before implementation.

## References

See REFERENCES.md.