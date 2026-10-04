"""Publication-grade visualization functions for reports and notebooks."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")  # Non-interactive headless backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

logger = logging.getLogger(__name__)

# Consistent aesthetic styling
sns.set_theme(style="whitegrid", font="sans-serif")
PALETTE = ["#2b5c8f", "#d95f02", "#7570b3", "#1b9e77"]


def plot_class_balance_and_tiers(
    tier1_df: pd.DataFrame,
    tier2_df: pd.DataFrame,
    output_path: str = "reports/figures/fig01_class_balance_and_data_loss.png",
) -> None:
    """Plot rating distribution and Tier 1 vs Tier 2 match sizes."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Panel 1: Rating breakdown (0-3)
    t1_counts = tier1_df["rating"].value_counts(normalize=True).sort_index()
    t2_counts = tier2_df["bechdel_rating"].value_counts(normalize=True).sort_index()

    idx = np.arange(4)
    width = 0.35

    labels = [
        "0: <2 Women",
        "1: No Talk",
        "2: Talk (Man only)",
        "3: Pass (Talk other)",
    ]

    axes[0].bar(idx - width / 2, t1_counts.values, width, label=f"Tier 1 (N={len(tier1_df)})", color="#3182bd")
    axes[0].bar(idx + width / 2, t2_counts.values, width, label=f"Tier 2 (N={len(tier2_df)})", color="#de2d26")
    axes[0].set_xticks(idx)
    axes[0].set_xticklabels(labels, rotation=15, ha="right")
    axes[0].set_ylabel("Proportion")
    axes[0].set_title("Bechdel Rating Distribution: Tier 1 vs Tier 2 Subset")
    axes[0].legend()

    # Panel 2: Dataset funnel / row counts
    stage_names = ["Tier 1 (Bechdel)", "Cornell Corpus", "Tier 2 (Matched)"]
    stage_counts = [len(tier1_df), 617, len(tier2_df)]
    colors = ["#2ca02c", "#ff7f0e", "#1f77b4"]

    bars = axes[1].bar(stage_names, stage_counts, color=colors, width=0.5)
    for bar in bars:
        h = bar.get_height()
        axes[1].annotate(
            f"{int(h):,}",
            xy=(bar.get_x() + bar.get_width() / 2, h),
            xytext=(0, 4),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontweight="bold",
        )
    axes[1].set_ylabel("Number of Films")
    axes[1].set_title("Dataset Ingestion & Tier Funnel")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_yearly_pass_rate_trend(
    tier1_df: pd.DataFrame,
    output_path: str = "reports/figures/fig02_yearly_pass_rate_trend.png",
) -> None:
    """Plot historical Bechdel pass rate over decades with sample counts."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    yearly = (
        tier1_df[(tier1_df["year"] >= 1930) & (tier1_df["year"] <= 2024)]
        .groupby("year")
        .agg(
            total=("pass", "count"),
            pass_rate=("pass", "mean"),
        )
        .reset_index()
    )

    # 5-year rolling average
    yearly["rolling_pass_rate"] = yearly["pass_rate"].rolling(window=5, min_periods=2).mean()

    fig, ax1 = plt.subplots(figsize=(11, 5))

    # Line plot: Pass rate
    ax1.plot(yearly["year"], yearly["pass_rate"], "o", color="#9ecae1", alpha=0.5, label="Annual Pass Rate")
    ax1.plot(yearly["year"], yearly["rolling_pass_rate"], "-", color="#08519c", linewidth=2.5, label="5-Year Moving Avg")
    ax1.axhline(0.5, color="gray", linestyle="--", alpha=0.6, label="50% Parity Line")
    ax1.set_xlabel("Release Year")
    ax1.set_ylabel("Bechdel Pass Rate (Fraction)", color="#08519c")
    ax1.set_ylim(0, 1.0)
    ax1.tick_params(axis="y", labelcolor="#08519c")

    # Bar plot on second axis: Annual film counts
    ax2 = ax1.twinx()
    ax2.bar(yearly["year"], yearly["total"], alpha=0.15, color="gray", width=0.8, label="Sample Size (Films/Yr)")
    ax2.set_ylabel("Film Count in Sample", color="gray")
    ax2.grid(False)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left")

    plt.title("Historical Trend of Bechdel Test Pass Rate (1930–2024, Tier 1)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_genre_representation(
    tier2_df: pd.DataFrame,
    output_path: str = "reports/figures/fig03_genre_representation.png",
) -> None:
    """Plot pass rate and volume across major film genres."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    genre_cols = [c for c in tier2_df.columns if c.startswith("genre_")]
    records = []
    for gcol in genre_cols:
        gname = gcol.replace("genre_", "").capitalize()
        sub = tier2_df[tier2_df[gcol] == 1]
        if len(sub) >= 10:
            records.append({
                "genre": gname,
                "n_films": len(sub),
                "pass_rate": sub["pass"].mean(),
            })

    if not records and "primary_genre" in tier2_df.columns:
        for gname, grp in tier2_df.groupby("primary_genre"):
            if len(grp) >= 5:
                records.append({
                    "genre": str(gname).capitalize(),
                    "n_films": len(grp),
                    "pass_rate": grp["pass"].mean(),
                })

    if not records:
        records.append({"genre": "All Films", "n_films": len(tier2_df), "pass_rate": float(tier2_df["pass"].mean())})

    gdf = pd.DataFrame(records).sort_values(by="pass_rate", ascending=True)

    fig, ax = plt.subplots(figsize=(9, 6))
    bars = ax.barh(gdf["genre"], gdf["pass_rate"], color="#2ca25f", height=0.6)
    ax.axvline(0.5, color="red", linestyle="--", alpha=0.7, label="50% Parity")

    for bar, n in zip(bars, gdf["n_films"]):
        w = bar.get_width()
        ax.text(
            w + 0.01,
            bar.get_y() + bar.get_height() / 2,
            f"{w:.1%} (N={n})",
            va="center",
            fontweight="bold",
            fontsize=9,
        )

    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Bechdel Pass Rate")
    ax.set_title("Bechdel Pass Rate by Genre (Tier 2 Corpus Subset)")
    ax.legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_correlation_matrix(
    tier2_df: pd.DataFrame,
    output_path: str = "reports/figures/fig04_correlation_matrix.png",
) -> None:
    """Plot correlation heatmap across key numerical representation variables."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    cols = [
        "pass", "female_line_share", "female_char_share", "num_ff_conversations",
        "longest_ff_exchange", "share_ff_lines_mentioning_men", "avg_male_talk_score_ff",
        "imdb_rating", "log_imdb_votes", "year"
    ]
    avail_cols = [c for c in cols if c in tier2_df.columns]
    corr = tier2_df[avail_cols].corr()

    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(
        corr,
        annot=True,
        fmt=".2f",
        cmap="coolwarm",
        vmin=-0.6,
        vmax=0.6,
        center=0,
        square=True,
        linewidths=0.5,
        ax=ax,
    )
    ax.set_title("Correlation Matrix of Dialogue, Metadata, and Bechdel Pass Target")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_regression_predictions(
    y_true: np.ndarray,
    y_pred: np.ndarray,
    title: str = "Actual vs. Predicted Female Dialogue Share",
    output_path: str = "reports/figures/fig05_regression_predictions.png",
) -> None:
    """Scatter plot with 45-degree reference line for regression evaluation."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(7, 6))
    ax.scatter(y_true, y_pred, alpha=0.5, color="#1f78b4", edgecolors="none")
    ax.plot([0, 1], [0, 1], "r--", linewidth=2, label="Perfect Fit (y = x)")

    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.set_xlabel("Actual Female Dialogue Share")
    ax.set_ylabel("Predicted Female Dialogue Share")
    ax.set_title(title)
    ax.legend()

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_confusion_matrices(
    cm_detector: np.ndarray,
    cm_ml: np.ndarray,
    ml_model_name: str = "Best ML Model",
    output_path: str = "reports/figures/fig07_confusion_matrices.png",
) -> None:
    """Side-by-side confusion matrix heatmaps comparing rule detector and ML model."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5))

    sns.heatmap(
        cm_detector,
        annot=True,
        fmt="d",
        cmap="Blues",
        ax=axes[0],
        xticklabels=["Fail (0)", "Pass (1)"],
        yticklabels=["Fail (0)", "Pass (1)"],
    )
    axes[0].set_title("Rule-Based Dialogue Detector\n(Stage A+B+C Rules)")
    axes[0].set_xlabel("Predicted Label")
    axes[0].set_ylabel("Ground Truth (Crowd)")

    sns.heatmap(
        cm_ml,
        annot=True,
        fmt="d",
        cmap="Purples",
        ax=axes[1],
        xticklabels=["Fail (0)", "Pass (1)"],
        yticklabels=["Fail (0)", "Pass (1)"],
    )
    axes[1].set_title(f"{ml_model_name}\n(Metadata + Dialogue Features)")
    axes[1].set_xlabel("Predicted Label")
    axes[1].set_ylabel("Ground Truth (Crowd)")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_feature_importance_and_shap(
    perm_df: pd.DataFrame,
    shap_df: pd.DataFrame,
    output_path: str = "reports/figures/fig08_feature_importance_shap.png",
) -> None:
    """Bar charts of Permutation Importance and SHAP values for best model."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(13, 6))

    top_perm = perm_df.head(10).sort_values(by="importance_mean", ascending=True)
    axes[0].barh(top_perm["feature"], top_perm["importance_mean"], color="#3182bd")
    axes[0].set_xlabel("Mean Decrease in F1 Score")
    axes[0].set_title("Top 10 Features: Permutation Importance")

    if not shap_df.empty and "mean_abs_shap" in shap_df.columns:
        top_shap = shap_df.head(10).sort_values(by="mean_abs_shap", ascending=True)
        feat_col = "feature" if "feature" in top_shap.columns else "feature_idx"
        axes[1].barh(top_shap[feat_col].astype(str), top_shap["mean_abs_shap"], color="#e6550d")
        axes[1].set_xlabel("Mean |SHAP Value| (Impact on Model Output)")
        axes[1].set_title("Top 10 Features: Mean |SHAP| Attribution")
    else:
        axes[1].text(0.5, 0.5, "SHAP data not available", ha="center")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def plot_fairness_slices(
    fairness_results: Dict[str, pd.DataFrame],
    output_path: str = "reports/figures/fig09_fairness_slices.png",
) -> None:
    """Plot model F1 score across demographic slices (Decade & Genre)."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Decade slice
    if "decade" in fairness_results and not fairness_results["decade"].empty:
        d_df = fairness_results["decade"].sort_values(by="group_value")
        colors = ["#de2d26" if row["significant_drop"] else "#2ca02c" for _, row in d_df.iterrows()]
        axes[0].bar(d_df["group_value"], d_df["f1"], color=colors, width=0.6)
        axes[0].axhline(d_df["f1"].mean(), color="black", linestyle="--", label="Slice Mean F1")
        axes[0].set_ylabel("F1 Score")
        axes[0].set_xlabel("Decade")
        axes[0].set_title("Fairness Audit: Model F1 by Decade\n(Red = Drop > 15%)")
        axes[0].set_ylim(0, 1.0)
        axes[0].legend()

    # Genre slice
    if "genre" in fairness_results and not fairness_results["genre"].empty:
        g_df = fairness_results["genre"].sort_values(by="f1", ascending=True)
        colors = ["#de2d26" if row["significant_drop"] else "#2ca02c" for _, row in g_df.iterrows()]
        axes[1].barh(g_df["group_value"], g_df["f1"], color=colors, height=0.6)
        axes[1].axvline(g_df["f1"].mean(), color="black", linestyle="--", label="Slice Mean F1")
        axes[1].set_xlabel("F1 Score")
        axes[1].set_title("Fairness Audit: Model F1 by Genre\n(Red = Drop > 15%)")
        axes[1].set_xlim(0, 1.0)
        axes[1].legend(loc="lower right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    logger.info(f"Saved figure to {output_path}")


def generate_all_report_figures(
    tier1_df: pd.DataFrame,
    tier2_df: pd.DataFrame,
    reg_y_true: np.ndarray,
    reg_y_pred: np.ndarray,
    cm_detector: np.ndarray,
    cm_ml: np.ndarray,
    ml_name: str,
    perm_df: pd.DataFrame,
    shap_df: pd.DataFrame,
    fairness_results: Dict[str, pd.DataFrame],
) -> None:
    """Generate and save all 8 report figures."""
    plot_class_balance_and_tiers(tier1_df, tier2_df)
    plot_yearly_pass_rate_trend(tier1_df)
    plot_genre_representation(tier2_df)
    plot_correlation_matrix(tier2_df)
    plot_regression_predictions(reg_y_true, reg_y_pred)
    plot_confusion_matrices(cm_detector, cm_ml, ml_model_name=ml_name)
    plot_feature_importance_and_shap(perm_df, shap_df)
    plot_fairness_slices(fairness_results)
