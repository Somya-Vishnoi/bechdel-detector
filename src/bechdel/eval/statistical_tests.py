"""Statistical hypothesis testing (Chi-Square, t-tests, Mann-Whitney U) and effect sizes.

All tests emphasize correlation, strictly rejecting causal interpretations.
"""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from scipy import stats

logger = logging.getLogger(__name__)

CAUSATION_DISCLAIMER = (
    "IMPORTANT: All observed associations represent observational correlations "
    "and strictly do NOT imply causal relationships. Confounding variables "
    "(such as era, studio budget, target audience, and genre conventions) "
    "substantially influence both representation and reception."
)


def compute_cramers_v(contingency_table: np.ndarray) -> float:
    """Calculate Cramér's V effect size for chi-square test."""
    chi2 = stats.chi2_contingency(contingency_table)[0]
    n = contingency_table.sum()
    r, c = contingency_table.shape
    min_dim = min(r - 1, c - 1)
    if min_dim == 0 or n == 0:
        return 0.0
    return float(np.sqrt(chi2 / (n * min_dim)))


def compute_cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Calculate Cohen's d effect size for two-sample difference."""
    n1, n2 = len(group1), len(group2)
    if n1 < 2 or n2 < 2:
        return 0.0
    s1 = np.var(group1, ddof=1)
    s2 = np.var(group2, ddof=1)
    s_pooled = np.sqrt(((n1 - 1) * s1 + (n2 - 1) * s2) / (n1 + n2 - 2))
    if s_pooled == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / s_pooled)


def run_chi_square_test(
    df: pd.DataFrame, factor_col: str, target_col: str = "pass"
) -> Dict[str, Any]:
    """Perform Chi-Square test of independence between a factor and the Bechdel pass rate."""
    clean_df = df.dropna(subset=[factor_col, target_col])
    contingency = pd.crosstab(clean_df[factor_col], clean_df[target_col])

    if contingency.empty or contingency.shape[0] < 2 or contingency.shape[1] < 2:
        return {
            "factor": factor_col,
            "error": "Insufficient levels for contingency table",
            "disclaimer": CAUSATION_DISCLAIMER,
        }

    chi2, p_val, dof, _ = stats.chi2_contingency(contingency)
    cramers_v = compute_cramers_v(contingency.values)

    pass_rates = clean_df.groupby(factor_col)[target_col].agg(["count", "mean"]).to_dict(orient="index")

    return {
        "factor": factor_col,
        "chi2_statistic": float(chi2),
        "p_value": float(p_val),
        "degrees_of_freedom": int(dof),
        "cramers_v": float(cramers_v),
        "significant_at_05": bool(p_val < 0.05),
        "pass_rates_by_group": pass_rates,
        "disclaimer": CAUSATION_DISCLAIMER,
    }


def run_two_sample_ttest(
    df: pd.DataFrame, continuous_col: str, group_col: str = "pass"
) -> Dict[str, Any]:
    """Perform independent two-sample t-test and Mann-Whitney U test."""
    clean_df = df.dropna(subset=[continuous_col, group_col])
    g0 = clean_df[clean_df[group_col] == 0][continuous_col].values.astype(float)
    g1 = clean_df[clean_df[group_col] == 1][continuous_col].values.astype(float)

    if len(g0) < 2 or len(g1) < 2:
        return {
            "variable": continuous_col,
            "error": "Insufficient sample size",
            "disclaimer": CAUSATION_DISCLAIMER,
        }

    t_stat, p_val_ttest = stats.ttest_ind(g1, g0, equal_var=False)
    u_stat, p_val_mwu = stats.mannwhitneyu(g1, g0, alternative="two-sided")
    cohen_d = compute_cohens_d(g1, g0)

    return {
        "variable": continuous_col,
        "mean_fail": float(np.mean(g0)),
        "std_fail": float(np.std(g0, ddof=1)),
        "mean_pass": float(np.mean(g1)),
        "std_pass": float(np.std(g1, ddof=1)),
        "t_statistic": float(t_stat),
        "p_value_ttest": float(p_val_ttest),
        "mann_whitney_u": float(u_stat),
        "p_value_mwu": float(p_val_mwu),
        "cohens_d": float(cohen_d),
        "significant_at_05": bool(p_val_ttest < 0.05),
        "disclaimer": CAUSATION_DISCLAIMER,
    }


def run_all_statistical_tests(tier1_df: pd.DataFrame, tier2_df: pd.DataFrame) -> Dict[str, Any]:
    """Execute complete suite of hypothesis tests across Tier 1 and Tier 2."""
    results = {}

    # 1. Chi-Square: Pass Rate vs Decade (Tier 1)
    results["chi2_decade_tier1"] = run_chi_square_test(tier1_df, "decade", "pass")

    # 2. Chi-Square: Pass Rate vs Decade (Tier 2)
    results["chi2_decade_tier2"] = run_chi_square_test(tier2_df, "decade", "pass")

    # 3. Chi-Square: Pass Rate vs Primary Genre (Tier 2)
    if "primary_genre" in tier2_df.columns:
        results["chi2_genre_tier2"] = run_chi_square_test(tier2_df, "primary_genre", "pass")

    # 4. Chi-Square: Pass Rate vs Female Character Presence (>= 2 women)
    if "stage_a_pass" in tier2_df.columns:
        results["chi2_stage_a_tier2"] = run_chi_square_test(tier2_df, "stage_a_pass", "pass")

    # 5. Two-Sample Tests: Female Line Share vs Pass
    if "female_line_share" in tier2_df.columns:
        results["ttest_female_line_share"] = run_two_sample_ttest(
            tier2_df, "female_line_share", "pass"
        )

    # 6. Two-Sample Tests: IMDb Rating vs Pass
    if "imdb_rating" in tier2_df.columns:
        results["ttest_imdb_rating"] = run_two_sample_ttest(
            tier2_df, "imdb_rating", "pass"
        )

    # 7. Two-Sample Tests: IMDb Votes vs Pass
    if "log_imdb_votes" in tier2_df.columns:
        results["ttest_imdb_votes"] = run_two_sample_ttest(
            tier2_df, "log_imdb_votes", "pass"
        )

    return results
