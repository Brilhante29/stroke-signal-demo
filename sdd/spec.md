# Spec: stroke-signal-demo

## Number

#4

## Claim

Este projeto prova que: reproducao de classificador clinico com dados sinteticos deterministicos, sem dependencia de dados reais ou infraestrutura externa.

## Stack

python, pandas, scikit-learn, matplotlib, docker

## User-visible output

- Docker command: `docker run --rm stroke-signal-demo`
- README opens with: `# #4 stroke-signal-demo`
- Benchmark table: accuracy, precision, recall, f1, confusion_matrix

## Scope

In:

- Implementar o menor produto funcional que prove o claim.
- Gerar dados sinteticos deterministicos que mimetizam features clinicas de AVC.
- Treinar classificador RandomForest com dados sinteticos.
- Reportar accuracy, precision, recall, f1 e matriz de confusao como JSON.
- Rodar por Docker.
- Gerar benchmark JSON reproduzivel.

Out:

- Publicar repo antes do primeiro resultado numerico.
- Depender de dados reais de pacientes.
- Depender de segredo pago para o caminho default.
- GPU ou deep learning.
- API de servico ou endpoint HTTP.

## Architecture

```
fixture (synthetic data) -> model (train + evaluate) -> benchmark (JSON output)
cli -> orchestrates pipeline
```

## Benchmark

Primary metric:

- name: accuracy
- target: first reproducible baseline >= 0.95
- command: `stroke-signal-demo benchmark --n-samples 5000 --seed 42 --output benchmarks/results/baseline.json`
- result file: `benchmarks/results/baseline.json`

## Dataset or fixture

- source: synthetic (src/stroke_signal/fixture.py)
- size: 5000 samples (configurable via --n-samples)
- license: project-specific (no external data)
- deterministic seed: 42

## Definition of done

- [x] Docker command works from clean clone.
- [x] README starts with project number and benchmark result.
- [x] Benchmark command writes JSON result.
- [x] Tests cover core behavior.
- [x] REFERENCES.md explains reuse.
- [x] No secret or paid credential required for default demo.
