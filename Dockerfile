FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml LICENSE ./
COPY src ./src
RUN pip install --no-cache-dir .

COPY tests ./tests
COPY benchmarks ./benchmarks
COPY project.yaml ./
COPY tools ./tools

ENTRYPOINT ["stroke-signal-demo"]
CMD ["benchmark", "--n-samples", "5000", "--seed", "42", "--output", "benchmarks/results/latest.json"]
