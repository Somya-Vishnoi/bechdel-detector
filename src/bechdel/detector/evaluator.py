"""Evaluation routines for rule-based Bechdel detector and stage-by-stage analysis."""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.metrics import (
    accuracy_score,
    cohen_kappa_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

logger = logging.getLogger(__name__)


def evaluate_binary_predictions(
    y_true: np.ndarray, y_pred: np.ndarray, prefix: str = ""
) -> Dict[str, Any]:
    """Compute comprehensive binary classification metrics."""
    cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
    tn, fp, fn, tp = cm.ravel() if cm.size == 4 else (0, 0, 0, 0)

    acc = float(accuracy_score(y_true, y_pred))
    prec = float(precision_score(y_true, y_pred, zero_division=0))
    rec = float(recall_score(y_true, y_pred, zero_division=0))
    f1 = float(f1_score(y_true, y_pred, zero_division=0))
    kappa = float(cohen_kappa_score(y_true, y_pred))
    spec = float(tn / (tn + fp)) if (tn + fp) > 0 else 0.0

    p = f"{prefix}_" if prefix else ""
    return {
        f"{p}accuracy": acc,
        f"{p}precision": prec,
        f"{p}recall": rec,
        f"{p}f1": f1,
        f"{p}specificity": spec,
        f"{p}cohen_kappa": kappa,
        f"{p}tn": int(tn),
        f"{p}fp": int(fp),
        f"{p}fn": int(fn),
        f"{p}tp": int(tp),
        f"{p}support": int(len(y_true)),
    }


def evaluate_detector_stages(
    film_results: List[Dict[str, Any]],
    tier2_df: pd.DataFrame,
    flagged_csv_path: str = "reports/flagged_conversations.csv",
    handcheck_csv_path: str = "reports/handcheck_sample.csv",
    random_seed: int = 42,
) -> Dict[str, Any]:
    """Evaluate detector vs crowd labels overall and at Stages A, B, and C.

    Stages:
    - Overall: detector_pass vs crowd pass (rating == 3)
    - Stage A: stage_a_pass vs crowd labels {0} vs {1,2,3}
    - Stage B: stage_b_pass vs crowd labels {1} vs {2,3}
    - Stage C: stage_c_pass vs crowd labels {2} vs {3}

    Also exports flagged conversations and a 50-row hand-check verification sample.
    """
    df_eval = pd.DataFrame(film_results)
    merged = pd.merge(
        tier2_df[["cornell_id", "bechdel_rating", "pass"]],
        df_eval,
        on="cornell_id"
    )

    y_true_overall = merged["pass"].values.astype(int)
    y_pred_overall = merged["detector_pass"].values.astype(int)
    overall_metrics = evaluate_binary_predictions(y_true_overall, y_pred_overall, prefix="overall")

    # Stage A: {0} vs {1, 2, 3}
    # True = has >= 2 women (rating in 1,2,3), False = rating == 0
    y_true_a = (merged["bechdel_rating"] >= 1).astype(int).values
    y_pred_a = merged["stage_a_pass"].astype(int).values
    stage_a_metrics = evaluate_binary_predictions(y_true_a, y_pred_a, prefix="stage_a")

    # Stage B: {1} vs {2, 3} (on subset of films with >= 2 women, ratings 1, 2, 3)
    df_stage_b = merged[merged["bechdel_rating"].isin([1, 2, 3])]
    if len(df_stage_b) > 0:
        y_true_b = (df_stage_b["bechdel_rating"] >= 2).astype(int).values
        y_pred_b = df_stage_b["stage_b_pass"].astype(int).values
        stage_b_metrics = evaluate_binary_predictions(y_true_b, y_pred_b, prefix="stage_b")
    else:
        stage_b_metrics = {}

    # Stage C: {2} vs {3} (on subset of films where women talk, ratings 2, 3)
    df_stage_c = merged[merged["bechdel_rating"].isin([2, 3])]
    if len(df_stage_c) > 0:
        y_true_c = (df_stage_c["bechdel_rating"] == 3).astype(int).values
        y_pred_c = df_stage_c["stage_c_pass"].astype(int).values
        stage_c_metrics = evaluate_binary_predictions(y_true_c, y_pred_c, prefix="stage_c")
    else:
        stage_c_metrics = {}

    # Export flagged conversations
    all_ff_convs = []
    for res in film_results:
        for conv in res.get("ff_conversations", []):
            all_ff_convs.append({
                "film_id": conv.film_id,
                "film_title": conv.film_title,
                "conv_id": conv.conv_id,
                "speaker_1": conv.char1_name,
                "speaker_2": conv.char2_name,
                "speaker_1_gender": conv.char1_gender,
                "speaker_2_gender": conv.char2_gender,
                "num_lines": conv.num_lines,
                "total_words": conv.total_words,
                "male_mentions": conv.male_mentions,
                "male_talk_score": round(conv.male_talk_score, 4),
                "flagged_about_man": int(conv.flagged_about_man),
                "text": conv.text.replace("\n", " ").replace("\r", " ").strip(),
            })

    df_convs = pd.DataFrame(all_ff_convs)
    flagged_file = Path(flagged_csv_path)
    flagged_file.parent.mkdir(parents=True, exist_ok=True)

    if not df_convs.empty:
        # Export all F-F conversations with flag status
        df_convs.to_csv(flagged_file, index=False)
        logger.info(f"Saved {len(df_convs)} F-F conversations to {flagged_file}")

        # Sample 50 flagged conversations for hand checking
        flagged_subset = df_convs[df_convs["flagged_about_man"] == 1]
        sample_size = min(50, len(flagged_subset)) if len(flagged_subset) >= 10 else min(50, len(df_convs))
        source_df = flagged_subset if len(flagged_subset) >= 10 else df_convs

        np.random.seed(random_seed)
        handcheck_sample = source_df.sample(n=sample_size, random_state=random_seed).copy()
        handcheck_sample["human_label"] = ""  # Empty column for manual verification
        cols = [
            "human_label", "film_title", "speaker_1", "speaker_2",
            "male_talk_score", "male_mentions", "total_words", "text", "film_id", "conv_id"
        ]
        handcheck_sample = handcheck_sample[[c for c in cols if c in handcheck_sample.columns]]
        handcheck_file = Path(handcheck_csv_path)
        handcheck_sample.to_csv(handcheck_file, index=False)
        logger.info(f"Saved {len(handcheck_sample)} verification rows to {handcheck_file}")
    else:
        logger.warning("No F-F conversations found to export.")

    return {
        "overall": overall_metrics,
        "stage_a": stage_a_metrics,
        "stage_b": stage_b_metrics,
        "stage_c": stage_c_metrics,
        "n_films": len(merged),
        "total_ff_conversations": len(df_convs),
    }
