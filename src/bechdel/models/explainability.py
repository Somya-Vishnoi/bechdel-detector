"""Model explainability using Permutation Importance and SHAP."""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.inspection import permutation_importance
import shap

logger = logging.getLogger(__name__)


def compute_permutation_importance(
    pipeline: Any,
    X: pd.DataFrame,
    y: np.ndarray,
    feature_names: List[str],
    scoring: str = "f1",
    n_repeats: int = 10,
    seed: int = 42,
) -> pd.DataFrame:
    """Compute permutation feature importance on fitted pipeline."""
    logger.info(f"Computing permutation importance ({scoring})...")
    res = permutation_importance(
        pipeline, X, y, scoring=scoring, n_repeats=n_repeats, random_state=seed
    )

    df_imp = pd.DataFrame({
        "feature": feature_names,
        "importance_mean": res.importances_mean,
        "importance_std": res.importances_std,
    }).sort_values(by="importance_mean", ascending=False)

    return df_imp.reset_index(drop=True)


def compute_shap_analysis(
    pipeline: Any,
    X: pd.DataFrame,
    feature_names: List[str],
    max_samples: int = 200,
    seed: int = 42,
) -> Dict[str, Any]:
    """Compute SHAP feature attributions on transformed feature matrix."""
    logger.info("Computing SHAP feature attributions...")
    prep = pipeline.named_steps.get("prep")
    clf = pipeline.named_steps.get("clf")

    # Transform features through preprocessor
    X_trans = prep.transform(X) if prep else X.values

    # Subsample if large for speed
    if len(X_trans) > max_samples:
        np.random.seed(seed)
        idx = np.random.choice(len(X_trans), size=max_samples, replace=False)
        X_sample = X_trans[idx]
    else:
        X_sample = X_trans

    shap_values = None
    mean_abs_shap = None

    try:
        if hasattr(clf, "feature_importances_"):
            # Tree-based model (RandomForest, HistGradientBoosting, DecisionTree)
            explainer = shap.TreeExplainer(clf)
            raw_shap = explainer.shap_values(X_sample)

            if isinstance(raw_shap, list):
                # Binary classification list: pick positive class (index 1)
                shap_values = raw_shap[1]
            elif isinstance(raw_shap, np.ndarray) and raw_shap.ndim == 3:
                shap_values = raw_shap[:, :, 1]
            else:
                shap_values = raw_shap

            mean_abs_shap = np.mean(np.abs(shap_values), axis=0)
        else:
            # Fallback to general Explainer
            explainer = shap.Explainer(clf.predict, X_sample)
            exp_res = explainer(X_sample)
            shap_values = exp_res.values
            mean_abs_shap = np.mean(np.abs(shap_values), axis=0)

        # Handle dimension mismatch if feature names count differs
        if len(feature_names) == len(mean_abs_shap):
            shap_df = pd.DataFrame({
                "feature": feature_names,
                "mean_abs_shap": mean_abs_shap,
            }).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)
        else:
            shap_df = pd.DataFrame({
                "feature_idx": range(len(mean_abs_shap)),
                "mean_abs_shap": mean_abs_shap,
            }).sort_values(by="mean_abs_shap", ascending=False).reset_index(drop=True)

    except Exception as e:
        logger.warning(f"SHAP explanation encountered error: {e}. Falling back gracefully.")
        shap_df = pd.DataFrame(columns=["feature", "mean_abs_shap"])

    return {
        "shap_summary_table": shap_df,
        "shap_values": shap_values,
        "sample_data": X_sample,
    }


def compute_explainability_artifacts(
    best_pipeline: Any,
    tier2_df: pd.DataFrame,
    feature_cols: List[str],
    seed: int = 42,
) -> Dict[str, Any]:
    """Execute both Permutation Importance and SHAP analyses on the best model."""
    X = tier2_df[feature_cols]
    y = tier2_df["pass"].values.astype(int)

    perm_df = compute_permutation_importance(
        best_pipeline, X, y, feature_names=feature_cols, seed=seed
    )

    shap_res = compute_shap_analysis(
        best_pipeline, X, feature_names=feature_cols, seed=seed
    )

    return {
        "permutation_importance": perm_df,
        "shap_summary": shap_res["shap_summary_table"],
        "shap_values": shap_res.get("shap_values"),
    }
