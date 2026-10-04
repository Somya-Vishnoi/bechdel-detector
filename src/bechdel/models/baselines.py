"""Baseline models for classification and regression benchmarking."""

import numpy as np
from sklearn.base import BaseEstimator, ClassifierMixin


class MajorityBaselineClassifier(BaseEstimator, ClassifierMixin):
    """Majority-class baseline classifier that always predicts the most frequent class."""

    def __init__(self):
        self.majority_class_ = None
        self.class_prob_ = None
        self.classes_ = np.array([0, 1])

    def fit(self, X, y):
        y_arr = np.asarray(y, dtype=int)
        counts = np.bincount(y_arr, minlength=2)
        self.majority_class_ = int(np.argmax(counts))
        self.class_prob_ = counts / len(y_arr)
        return self

    def predict(self, X):
        n_samples = len(X)
        return np.full(n_samples, self.majority_class_, dtype=int)

    def predict_proba(self, X):
        n_samples = len(X)
        probs = np.tile(self.class_prob_, (n_samples, 1))
        return probs
