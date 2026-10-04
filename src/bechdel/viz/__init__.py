"""Visualization package for producing publication-quality charts and reports figures."""

from bechdel.viz.plots import (
    plot_class_balance_and_tiers,
    plot_yearly_pass_rate_trend,
    plot_genre_representation,
    plot_correlation_matrix,
    plot_regression_predictions,
    plot_confusion_matrices,
    plot_feature_importance_and_shap,
    plot_fairness_slices,
    generate_all_report_figures,
)

__all__ = [
    "plot_class_balance_and_tiers",
    "plot_yearly_pass_rate_trend",
    "plot_genre_representation",
    "plot_correlation_matrix",
    "plot_regression_predictions",
    "plot_confusion_matrices",
    "plot_feature_importance_and_shap",
    "plot_fairness_slices",
    "generate_all_report_figures",
]
