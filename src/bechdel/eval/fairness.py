"""Fairness and demographic performance auditing across genre, decade, and subgroups."""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score

logger = logging.getLogger(__name__)


def audit_subgroup_performance(
    df: pd.DataFrame,
    group_col: str,
    y_true_col: str = "pass",
    y_pred_col: str = "pred",
    min_support: int = 10,
) -> pd.DataFrame:
    """Evaluate classification performance across distinct subgroup slices."""
    records = []
    overall_f1 = f1_score(df[y_true_col], df[y_pred_col], zero_division=0)
    overall_rec = recall_score(df[y_true_col], df[y_pred_col], zero_division=0)

    for group_val, grp in df.groupby(group_col):
        n = len(grp)
        if n < min_support:
            continue

        y_true = grp[y_true_col].values
        y_pred = grp[y_pred_col].values

        acc = accuracy_score(y_true, y_pred)
        prec = precision_score(y_true, y_pred, zero_division=0)
        rec = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        pass_rate = float(np.mean(y_true))
        f1_drop = float(overall_f1 - f1)
        rec_drop = float(overall_rec - rec)

        records.append({
            "group_feature": group_col,
            "group_value": str(group_val),
            "support": n,
            "ground_truth_pass_rate": round(pass_rate, 4),
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "f1_drop_from_overall": round(f1_drop, 4),
            "recall_drop_from_overall": round(rec_drop, 4),
            "significant_drop": bool(f1_drop > 0.15 or rec_drop > 0.15),
        })

    return pd.DataFrame(records)


def audit_model_fairness(
    df: pd.DataFrame,
    y_true_col: str = "pass",
    y_pred_col: str = "pred",
) -> Dict[str, pd.DataFrame]:
    """Audit model fairness across all eligible demographic and metadata dimensions."""
    audit_results = {}

    # 1. By Decade
    if "decade" in df.columns:
        audit_results["decade"] = audit_subgroup_performance(
            df, "decade", y_true_col=y_true_col, y_pred_col=y_pred_col, min_support=10
        )

    # 2. By Primary Genre
    if "primary_genre" in df.columns:
        audit_results["genre"] = audit_subgroup_performance(
            df, "primary_genre", y_true_col=y_true_col, y_pred_col=y_pred_col, min_support=10
        )

    # 3. By Language (if populated)
    if "language" in df.columns and df["language"].notna().sum() > 20:
        audit_results["language"] = audit_subgroup_performance(
            df, "language", y_true_col=y_true_col, y_pred_col=y_pred_col, min_support=10
        )

    return audit_results
