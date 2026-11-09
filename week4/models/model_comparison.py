#!/usr/bin/env python3
"""Compare Isolation Forest and Random Forest on offline CAN windows."""

from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import StandardScaler

from week2.pipeline import FEATURES, vectorize


def compare_models(training_windows, test_windows):
    if not training_windows or not test_windows:
        raise ValueError("Training and test windows must not be empty")

    X_train = vectorize(training_windows, FEATURES)
    X_test = vectorize(test_windows, FEATURES)

    y_train = [row["label"] for row in training_windows]
    y_test = [row["label"] for row in test_windows]

    if len(set(y_train)) < 2:
        raise ValueError("Random Forest requires normal and injected training examples")

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    models = {
        "Isolation Forest": IsolationForest(
            n_estimators=250,
            contamination=0.10,
            random_state=42
        ),
        "Random Forest": RandomForestClassifier(
            n_estimators=200,
            class_weight="balanced",
            random_state=42
        ),
    }

    results = {}

    for name, model in models.items():
        if name == "Isolation Forest":
            model.fit(X_train_scaled)
            predictions = [0 if value == 1 else 1
                           for value in model.predict(X_test_scaled)]
        else:
            model.fit(X_train_scaled, y_train)
            predictions = model.predict(X_test_scaled).tolist()

        results[name] = {
            "confusion_matrix": confusion_matrix(
                y_test, predictions, labels=[0, 1]
            ).tolist(),
            "classification_report": classification_report(
                y_test,
                predictions,
                labels=[0, 1],
                target_names=["normal", "synthetic_injected"],
                zero_division=0,
                output_dict=True
            ),
        }

    return results
