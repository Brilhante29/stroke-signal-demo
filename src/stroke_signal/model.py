from __future__ import annotations

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split


def train_and_evaluate(
    df: pd.DataFrame,
    seed: int = 42,
    test_size: float = 0.2,
) -> dict:
    feature_cols = [
        "age",
        "hypertension",
        "heart_disease",
        "avg_glucose_level",
        "bmi",
        "gender",
        "ever_married",
    ]
    X = df[feature_cols]
    y = df["stroke"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=seed, stratify=y
    )

    clf = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=seed,
        class_weight="balanced",
        n_jobs=1,
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)

    cm = confusion_matrix(y_test, y_pred).tolist()

    return {
        "accuracy": float(accuracy_score(y_test, y_pred)),
        "confusion_matrix": cm,
        "precision": float(precision_score(y_test, y_pred, zero_division=0)),
        "recall": float(recall_score(y_test, y_pred, zero_division=0)),
        "f1": float(f1_score(y_test, y_pred, zero_division=0)),
        "n_train": len(X_train),
        "n_test": len(X_test),
    }
