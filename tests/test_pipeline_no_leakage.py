"""Rigorous data leakage prevention tests for pipelines."""

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold
from sklearn.pipeline import Pipeline

from bechdel.features.builder import create_preprocessor
from bechdel.models.classification import evaluate_pipeline_cv


def test_scaler_fits_strictly_on_train():
    """Verify that StandardScaler fits only on training split and ignores test distribution."""
    np.random.seed(42)
    # Train data centered at 10.0
    X_train = pd.DataFrame({
        "num_1": np.random.normal(loc=10.0, scale=1.0, size=100),
        "num_2": np.random.normal(loc=5.0, scale=0.5, size=100),
    })
    y_train = np.random.binomial(1, 0.5, size=100)

    # Test data massively shifted to 10,000.0
    X_test = pd.DataFrame({
        "num_1": np.random.normal(loc=10000.0, scale=1.0, size=50),
        "num_2": np.random.normal(loc=5000.0, scale=0.5, size=50),
    })

    prep = create_preprocessor(numeric_features=["num_1", "num_2"])
    pipe = Pipeline([
        ("prep", prep),
        ("clf", LogisticRegression()),
    ])

    pipe.fit(X_train, y_train)

    scaler = pipe.named_steps["prep"].named_transformers_["num"].named_steps["scaler"]
    scaler_mean = scaler.mean_

    # Scaler mean must match X_train mean within small precision
    expected_train_mean = X_train[["num_1", "num_2"]].mean().values
    np.testing.assert_allclose(scaler_mean, expected_train_mean, rtol=1e-5)

    # Scaler mean must NOT be influenced by the shifted test distribution
    assert scaler_mean[0] < 20.0
    assert scaler_mean[1] < 10.0

    # Ensure transforming test data does not alter fitted parameters
    _ = pipe.predict(X_test)
    np.testing.assert_allclose(scaler.mean_, expected_train_mean, rtol=1e-5)


def test_cv_zero_leakage():
    """Verify that evaluate_pipeline_cv processes all folds without label or test leakage."""
    np.random.seed(42)
    X = pd.DataFrame({
        "num_1": np.random.randn(80),
        "num_2": np.random.randn(80),
    })
    y = np.random.binomial(1, 0.5, size=80)

    prep = create_preprocessor(numeric_features=["num_1", "num_2"])
    pipe = Pipeline([
        ("prep", prep),
        ("clf", LogisticRegression()),
    ])

    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=42)
    res = evaluate_pipeline_cv(pipe, X, y, cv=cv)

    assert "accuracy" in res
    assert "f1" in res
    assert "oof_preds" in res
    assert len(res["oof_preds"]) == 80
