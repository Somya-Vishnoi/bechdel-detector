"""Classification pipelines with zero-leakage cross-validation and temporal splits."""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier

from bechdel.eval.metrics import evaluate_classification_predictions
from bechdel.features.builder import (
    create_preprocessor,
    get_dialogue_feature_names,
    get_metadata_feature_names,
)
from bechdel.models.baselines import MajorityBaselineClassifier

logger = logging.getLogger(__name__)


def get_classification_model_zoo(seed: int = 42) -> Dict[str, Any]:
    """Instantiate the 6 required classification model families plus baselines."""
    return {
        "MajorityBaseline": MajorityBaselineClassifier(),
        "LogisticRegression": LogisticRegression(
            class_weight="balanced", max_iter=1000, random_state=seed
        ),
        "KNN": KNeighborsClassifier(n_neighbors=7),
        "NaiveBayes": GaussianNB(),
        "DecisionTree": DecisionTreeClassifier(
            class_weight="balanced", max_depth=5, min_samples_leaf=5, random_state=seed
        ),
        "SVM": SVC(
            class_weight="balanced", probability=True, kernel="rbf", C=1.0, random_state=seed
        ),
        "RandomForest": RandomForestClassifier(
            class_weight="balanced", n_estimators=100, max_depth=6, random_state=seed
        ),
        "HistGradientBoosting": HistGradientBoostingClassifier(
            class_weight="balanced", max_depth=4, random_state=seed
        ),
    }


def evaluate_pipeline_cv(
    pipeline: Pipeline,
    X: pd.DataFrame,
    y: np.ndarray,
    cv: StratifiedKFold,
) -> Dict[str, Any]:
    """Execute cross-validation with zero data leakage (pipeline fits inside each fold)."""
    oof_preds = np.zeros(len(y), dtype=int)
    oof_probs = np.zeros(len(y), dtype=float)

    for train_idx, val_idx in cv.split(X, y):
        X_train, X_val = X.iloc[train_idx], X.iloc[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]

        pipeline.fit(X_train, y_train)

        oof_preds[val_idx] = pipeline.predict(X_val)
        if hasattr(pipeline, "predict_proba"):
            probs = pipeline.predict_proba(X_val)
            oof_probs[val_idx] = probs[:, 1] if probs.ndim == 2 else probs
        else:
            oof_probs[val_idx] = oof_preds[val_idx]

    metrics = evaluate_classification_predictions(y, oof_preds, oof_probs)
    return {
        **metrics,
        "oof_preds": oof_preds,
        "oof_probs": oof_probs,
    }


def evaluate_pipeline_temporal_split(
    pipeline: Pipeline,
    X: pd.DataFrame,
    y: np.ndarray,
    years: np.ndarray,
    split_year: int = 2000,
) -> Dict[str, Any]:
    """Train on historical films (year <= split_year) and evaluate on modern films."""
    train_mask = years <= split_year
    test_mask = years > split_year

    if train_mask.sum() == 0 or test_mask.sum() == 0:
        logger.warning(f"Temporal split year {split_year} created empty train or test partition.")
        return {}

    X_train, X_test = X[train_mask], X[test_mask]
    y_train, y_test = y[train_mask], y[test_mask]

    pipeline.fit(X_train, y_train)

    test_preds = pipeline.predict(X_test)
    test_probs = None
    if hasattr(pipeline, "predict_proba"):
        probs = pipeline.predict_proba(X_test)
        test_probs = probs[:, 1] if probs.ndim == 2 else probs
    else:
        test_probs = test_preds

    metrics = evaluate_classification_predictions(y_test, test_preds, test_probs)
    metrics["n_train"] = int(train_mask.sum())
    metrics["n_test"] = int(test_mask.sum())
    metrics["split_year"] = split_year
    metrics["test_preds"] = test_preds
    metrics["test_indices"] = np.where(test_mask)[0]
    return metrics


def run_classification_experiments(
    tier2_df: pd.DataFrame,
    seed: int = 42,
    n_splits: int = 5,
    temporal_split_year: int = 2000,
) -> Dict[str, Any]:
    """Run full suite of classification experiments.

    Experiments:
    1. Majority-class baseline
    2. Metadata-only models (Tier 2 subset)
    3. Metadata + Dialogue/Detector features (Tier 2 subset)
    Across both Stratified 5-Fold CV and Temporal Split.
    """
    logger.info("Setting up classification experiments...")
    y = tier2_df["pass"].values.astype(int)
    years = tier2_df["year"].values.astype(int)

    metadata_cols = [c for c in get_metadata_feature_names() if c in tier2_df.columns]
    dialogue_cols = [c for c in get_dialogue_feature_names() if c in tier2_df.columns]
    combined_cols = metadata_cols + dialogue_cols

    cv = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=seed)

    experiment_definitions = {
        "Exp1_Baseline": {
            "features": metadata_cols,
            "models": {"MajorityBaseline": MajorityBaselineClassifier()},
        },
        "Exp2_Metadata_Only": {
            "features": metadata_cols,
            "models": get_classification_model_zoo(seed=seed),
        },
        "Exp3_Metadata_Plus_Dialogue": {
            "features": combined_cols,
            "models": get_classification_model_zoo(seed=seed),
        },
    }

    results_table_rows = []
    full_models_cv = {}
    full_models_temporal = {}
    fitted_pipelines = {}

    for exp_name, exp_cfg in experiment_definitions.items():
        feat_cols = exp_cfg["features"]
        X_df = tier2_df[feat_cols].copy()
        prep = create_preprocessor(numeric_features=feat_cols)

        for model_name, model in exp_cfg["models"].items():
            run_key = f"{exp_name}__{model_name}"
            pipe = Pipeline([
                ("prep", prep),
                ("clf", model),
            ])

            # 1. Stratified K-Fold CV
            cv_res = evaluate_pipeline_cv(pipe, X_df, y, cv=cv)
            full_models_cv[run_key] = cv_res

            # 2. Temporal Split
            temp_res = evaluate_pipeline_temporal_split(
                pipe, X_df, y, years=years, split_year=temporal_split_year
            )
            full_models_temporal[run_key] = temp_res

            # Fit on full dataset for serialization / explainability
            pipe.fit(X_df, y)
            fitted_pipelines[run_key] = pipe

            results_table_rows.append({
                "experiment": exp_name,
                "model": model_name,
                "feature_set": "metadata" if "Metadata_Only" in exp_name else ("dialogue+metadata" if "Dialogue" in exp_name else "none"),
                "cv_accuracy": round(cv_res["accuracy"], 4),
                "cv_f1": round(cv_res["f1"], 4),
                "cv_pr_auc": round(cv_res["pr_auc"], 4) if cv_res.get("pr_auc") is not None else None,
                "cv_roc_auc": round(cv_res["roc_auc"], 4) if cv_res.get("roc_auc") is not None else None,
                "cv_precision": round(cv_res["precision"], 4),
                "cv_recall": round(cv_res["recall"], 4),
                "cv_cohen_kappa": round(cv_res["cohen_kappa"], 4),
                "temp_accuracy": round(temp_res.get("accuracy", 0.0), 4),
                "temp_f1": round(temp_res.get("f1", 0.0), 4),
                "temp_pr_auc": round(temp_res.get("pr_auc", 0.0), 4) if temp_res.get("pr_auc") is not None else None,
                "temp_roc_auc": round(temp_res.get("roc_auc", 0.0), 4) if temp_res.get("roc_auc") is not None else None,
                "temp_recall": round(temp_res.get("recall", 0.0), 4),
            })

    summary_df = pd.DataFrame(results_table_rows).sort_values(by="cv_f1", ascending=False)
    logger.info("Classification experiments complete.")

    # Find the top-performing model
    best_row = summary_df.iloc[0]
    best_key = f"{best_row['experiment']}__{best_row['model']}"
    best_pipeline = fitted_pipelines[best_key]

    return {
        "summary_table": summary_df,
        "cv_results": full_models_cv,
        "temporal_results": full_models_temporal,
        "fitted_pipelines": fitted_pipelines,
        "best_model_key": best_key,
        "best_pipeline": best_pipeline,
        "metadata_features": metadata_cols,
        "combined_features": combined_cols,
    }
