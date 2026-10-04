"""Regression models and evaluation for representation targets."""

import logging
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from bechdel.eval.metrics import evaluate_regression_predictions

logger = logging.getLogger(__name__)


def train_female_dialogue_share_regressors(
    tier2_df: pd.DataFrame,
    feature_cols: Optional[List[str]] = None,
    seed: int = 42,
    n_splits: int = 5,
) -> Dict[str, Any]:
    """Train and evaluate regressors predicting female dialogue share per film."""
    target_col = "female_line_share"
    if target_col not in tier2_df.columns:
        raise ValueError(f"Target column '{target_col}' not found in Tier 2 dataset.")

    df = tier2_df.dropna(subset=[target_col]).copy()
    if feature_cols is None:
        # Predict using metadata features (year, ratings, votes, genres, cast)
        feature_cols = ["year", "imdb_rating", "log_imdb_votes", "female_char_share"]
        genre_cols = [c for c in df.columns if c.startswith("genre_")]
        feature_cols.extend(genre_cols)

    X = df[feature_cols].copy()
    y = df[target_col].values

    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=seed),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=100, max_depth=6, random_state=seed
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            n_estimators=100, max_depth=3, learning_rate=0.05, random_state=seed
        ),
    }

    kf = KFold(n_splits=n_splits, shuffle=True, random_state=seed)
    results = {}

    for name, model in models.items():
        pipe = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
            ("regressor", model),
        ])

        y_pred = cross_val_predict(pipe, X, y, cv=kf)
        metrics = evaluate_regression_predictions(y, y_pred)
        results[name] = {
            **metrics,
            "n_samples": len(y),
            "features_used": feature_cols,
        }
        logger.info(
            f"Regressor {name} on dialogue share -> RMSE: {metrics['rmse']:.4f}, R2: {metrics['r2']:.4f}"
        )

    return results


def train_yearly_pass_rate_trend_regressors(
    tier1_df: pd.DataFrame,
    min_films_per_year: int = 15,
    seed: int = 42,
) -> Dict[str, Any]:
    """Train and evaluate models forecasting the historical yearly Bechdel pass rate."""
    yearly = (
        tier1_df.groupby("year")
        .agg(
            total_films=("pass", "count"),
            pass_rate=("pass", "mean")
        )
        .reset_index()
    )

    # Filter years with sufficient sample size
    yearly = yearly[yearly["total_films"] >= min_films_per_year].copy()
    yearly["year_sq"] = yearly["year"] ** 2

    X = yearly[["year", "year_sq"]].values
    y = yearly["pass_rate"].values

    models = {
        "LinearRegression": LinearRegression(),
        "Ridge": Ridge(alpha=1.0, random_state=seed),
        "RandomForestRegressor": RandomForestRegressor(
            n_estimators=50, max_depth=4, random_state=seed
        ),
        "GradientBoostingRegressor": GradientBoostingRegressor(
            n_estimators=50, max_depth=3, learning_rate=0.05, random_state=seed
        ),
    }

    kf = KFold(n_splits=5, shuffle=True, random_state=seed)
    results = {}

    for name, model in models.items():
        pipe = Pipeline([
            ("scaler", StandardScaler()),
            ("regressor", model),
        ])
        y_pred = cross_val_predict(pipe, X, y, cv=kf)
        metrics = evaluate_regression_predictions(y, y_pred)
        results[name] = {
            **metrics,
            "n_years": len(y),
        }
        logger.info(
            f"Regressor {name} on yearly pass rate -> RMSE: {metrics['rmse']:.4f}, R2: {metrics['r2']:.4f}"
        )

    return {
        "yearly_data": yearly.to_dict(orient="records"),
        "models": results,
    }


def train_regression_models(
    tier1_df: pd.DataFrame,
    tier2_df: pd.DataFrame,
    seed: int = 42,
) -> Dict[str, Any]:
    """Run all required regression experiments."""
    return {
        "dialogue_share_regression": train_female_dialogue_share_regressors(tier2_df, seed=seed),
        "yearly_trend_regression": train_yearly_pass_rate_trend_regressors(tier1_df, seed=seed),
    }
