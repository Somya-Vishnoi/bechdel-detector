"""Evaluation metrics, fairness auditing, and statistical hypothesis testing."""

from bechdel.eval.metrics import (
    evaluate_classification_predictions,
    evaluate_regression_predictions,
)
from bechdel.eval.statistical_tests import (
    run_chi_square_test,
    run_two_sample_ttest,
    run_all_statistical_tests,
)
from bechdel.eval.fairness import audit_model_fairness
from bechdel.eval.error_analysis import perform_error_analysis

__all__ = [
    "evaluate_classification_predictions",
    "evaluate_regression_predictions",
    "run_chi_square_test",
    "run_two_sample_ttest",
    "run_all_statistical_tests",
    "audit_model_fairness",
    "perform_error_analysis",
]
