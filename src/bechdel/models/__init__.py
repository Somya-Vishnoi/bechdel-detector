"""Models package: baselines, regression, classification, and explainability."""

from bechdel.models.baselines import MajorityBaselineClassifier
from bechdel.models.regression import train_regression_models
from bechdel.models.classification import run_classification_experiments
from bechdel.models.explainability import compute_explainability_artifacts

__all__ = [
    "MajorityBaselineClassifier",
    "train_regression_models",
    "run_classification_experiments",
    "compute_explainability_artifacts",
]
