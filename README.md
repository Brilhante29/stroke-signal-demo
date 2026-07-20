# #4 stroke-signal-demo

**Status:** benchmarked

**Proves:** reproducao de classificador clinico com dados sinteticos deterministicos.

**Benchmark:** `accuracy`, confusion matrix baseline versionado em [`benchmarks/results/baseline.json`](benchmarks/results/baseline.json).

| Metric | Value | Unit |
|---|---|---:|
| accuracy | 0.987 | unit |
| precision | 0.863 | unit |
| recall | 0.880 | unit |
| f1_score | 0.871 | unit |

**Baseline:** accuracy `0.987`, `5000` synthetic samples, seed `42`, RandomForest `100` estimators. O JSON versionado registra ambiente, comando e matriz de confusao.

## 1. O que roda

Um pipeline de tres estagios:

1. Gerador de dados sinteticos que simula features de risco de AVC (idade, hypertension, heart disease, glicose, IMC)
2. Classificador RandomForest com `class_weight="balanced"` para lidar com desbalanceamento (5% stroke)
3. Benchmark que reporta accuracy, precision, recall, f1 e matriz de confusao

O caminho padrao e local-first e broker-free: todos os dados sao sinteticos e deterministicos.

## 2. Stack e decisoes

- Python 3.12, pandas, scikit-learn, matplotlib
- RandomForestClassifier com `n_estimators=100`, `max_depth=10`
- Dados sinteticos com seed deterministica (`sklearn.ensemble`)
- CLI argparse com subcomandos `demo` e `benchmark`
- Docker multistage com imagem `python:3.12-slim`
- Nao ha dependencia de rede, banco, GPU ou servico pago

## 3. Execucao

Local:

```bash
pip install -e .
stroke-signal-demo demo
stroke-signal-demo benchmark --n-samples 5000 --seed 42 --output benchmarks/results/latest.json
```

Docker:

```bash
docker build -t stroke-signal-demo .
docker run --rm stroke-signal-demo demo
docker run --rm -v "${PWD}/benchmarks/results:/app/benchmarks/results" stroke-signal-demo benchmark --output /app/benchmarks/results/latest.json
```

## 4. Dados sinteticos

O fixture gera 7 features que correlacionam com risco de AVC:

- `age`: distribuicao uniforme [0, 100]
- `hypertension`: binomial com correlacao com idade
- `heart_disease`: binomial com correlacao com idade
- `avg_glucose_level`: lognormal
- `bmi`: normal (media 26, desvio 5)
- `gender`: binomial 50%
- `ever_married`: binomial 70% para idade > 18

Rotulo `stroke`: ~5% da amostra, gerado por modelo logistico com features acima.
