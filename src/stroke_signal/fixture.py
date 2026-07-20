from __future__ import annotations

import numpy as np
import pandas as pd


def generate_dataset(
    n_samples: int = 5000,
    seed: int = 42,
    stroke_ratio: float = 0.05,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    age = rng.uniform(0, 100, size=n_samples)
    hypertension = rng.binomial(1, 0.08 + 0.002 * age, size=n_samples)
    heart_disease = rng.binomial(1, 0.04 + 0.001 * age, size=n_samples)
    avg_glucose_level = rng.lognormal(mean=4.5, sigma=0.4, size=n_samples)
    bmi = rng.normal(loc=26, scale=5, size=n_samples)
    gender = rng.binomial(1, 0.5, size=n_samples)
    ever_married = (age > 18).astype(int) * rng.binomial(1, 0.7, size=n_samples)

    base_risk = (
        -6.0
        + 0.06 * age
        + 1.5 * hypertension
        + 1.2 * heart_disease
        + 0.3 * (avg_glucose_level - 100) / 50
        + 0.05 * (bmi - 25)
    )

    stroke_prob = 1.0 / (1.0 + np.exp(-base_risk))
    stroke_prob = np.clip(stroke_prob, 0, 1)

    target_ratio = stroke_ratio
    if np.mean(stroke_prob) > target_ratio:
        scale = np.percentile(stroke_prob, 100 * (1 - target_ratio))
        stroke = (stroke_prob > scale).astype(int)
    else:
        stroke = rng.binomial(1, stroke_prob)

    return pd.DataFrame({
        "age": age,
        "hypertension": hypertension,
        "heart_disease": heart_disease,
        "avg_glucose_level": avg_glucose_level,
        "bmi": bmi,
        "gender": gender,
        "ever_married": ever_married,
        "stroke": stroke,
    })
