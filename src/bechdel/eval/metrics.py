"""Comprehensive metrics calculation for classification and regression models."""

import logging
from typing import Any, Dict, Optional
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    average_precision_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    log_loss,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)

logger = logging.getLogger(__name__)


def evaluate_classification_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    y_prob: Optional[np.ndarray] = None,
) -> Dict[str, Any]:
    """Calculate all standard classification metrics.

    Metrics:
    - Accuracy, Log Loss, ROC-AUC, PR-AUC (Average Precision), Precision, Recall, F1
    - Confusion Matrix (TN, FP, FN, TP)
    - Cohen's Kappa
    """
    y_true = np.asarray(y_true, dtype=int)
    y_pred = np.asarray(y_pred, dtype=int)

    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    kappa = float(cohen_kappa_score(y_true, y_pred))

    metrics: Dict[str, Any] = {
        "accuracy": acc,
        "precision": prec,
        "recall": rec,
        "f1": f1,
        "cohen_kappa": kappa,
        "confusion_matrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp),
        },
        "support": int(len(y_true)),
    }

    if y_prob is not None:
        y_prob = np.asarray(y_prob, dtype=float)
        # Handle 2D probability outputs
        if y_prob.ndim == 2:
            y_prob_pos = y_prob[:, 1]
        else:
            y_prob_pos = y_prob

        # Clip probabilities for stable log loss
        clipped_prob = np.clip(y_prob_pos, 1e-15, 1 - 1e-15)

        try:
            metrics["log_loss"] = float(log_loss(y_true, clipped_prob))
        except Exception:
            metrics["log_loss"] = None

        try:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob_pos))
        except Exception:
            metrics["roc_auc"] = None

        try:
            metrics["pr_auc"] = float(average_precision_score(y_true, y_prob_pos))
        except Exception:
            metrics["pr_auc"] = None
    else:
        metrics["log_loss"] = None
        metrics["roc_auc"] = None
        metrics["pr_auc"] = None

    return metrics


def evaluate_regression_predictions(
    y_true: np.ndarray, y_pred: np.ndarray
) -> Dict[str, float]:
    """Calculate standard regression metrics: MAE, MSE, RMSE, R2."""
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)

    mae = float(mean_absolute_error(y_true, y_pred))
    mse = float(mean_squared_error(y_true, y_pred))
    rmse = float(np.sqrt(mse))
    r2 = float(r2_score(y_true, y_pred))

    return {
        "mae": mae,
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
    }
