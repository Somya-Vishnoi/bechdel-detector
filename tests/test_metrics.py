"""Tests for evaluation metrics and statistical calculations."""

import numpy as np
import pytest
from bechdel.eval.metrics import (
    evaluate_classification_predictions,
    evaluate_regression_predictions,
)


def test_classification_metrics_perfect_predictions():
    y_true = np.array([1, 0, 1, 1, 0, 0])
    y_pred = np.array([1, 0, 1, 1, 0, 0])
    y_prob = np.array([0.9, 0.1, 0.8, 0.95, 0.05, 0.2])

    metrics = evaluate_classification_predictions(y_true, y_pred, y_prob)

    assert metrics["accuracy"] == 1.0
    assert metrics["precision"] == 1.0
    assert metrics["recall"] == 1.0
    assert metrics["f1"] == 1.0
    assert metrics["cohen_kappa"] == 1.0
    assert metrics["roc_auc"] == 1.0
    assert metrics["pr_auc"] == 1.0
    assert metrics["confusion_matrix"]["tp"] == 3
    assert metrics["confusion_matrix"]["tn"] == 3
    assert metrics["confusion_matrix"]["fp"] == 0
    assert metrics["confusion_matrix"]["fn"] == 0


def test_classification_metrics_imperfect_predictions():
    y_true = np.array([1, 1, 0, 0])
    y_pred = np.array([1, 0, 0, 1])
    # TP=1, FN=1, TN=1, FP=1
    metrics = evaluate_classification_predictions(y_true, y_pred)

    assert metrics["accuracy"] == 0.5
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.5
    assert metrics["f1"] == 0.5
    assert metrics["cohen_kappa"] == 0.0


def test_regression_metrics():
    y_true = np.array([1.0, 2.0, 3.0, 4.0])
    y_pred = np.array([1.0, 2.0, 3.0, 5.0])  # Error on last item = 1.0

    metrics = evaluate_regression_predictions(y_true, y_pred)

    assert metrics["mae"] == 0.25
    assert metrics["mse"] == 0.25
    assert metrics["rmse"] == 0.5
    assert metrics["r2"] > 0.0
