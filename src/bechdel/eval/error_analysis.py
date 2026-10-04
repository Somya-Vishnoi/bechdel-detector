"""Error analysis: qualitative inspection of detector vs crowd discrepancies."""

import logging
from pathlib import Path
from typing import Any, Dict, List
import pandas as pd

logger = logging.getLogger(__name__)


def perform_error_analysis(
    tier2_df: pd.DataFrame,
    detector_results: List[Dict[str, Any]],
    output_path: str = "reports/error_analysis_top20.csv",
) -> Dict[str, pd.DataFrame]:
    """Identify and analyze top 20 False Positives and top 20 False Negatives.

    Discrepancy taxonomy:
    - FP: Detector says Pass (1), Crowd says Fail (0).
    - FN: Detector says Fail (0), Crowd says Pass (1).
    """
    df_det = pd.DataFrame(detector_results)
    det_cols = [
        "cornell_id", "detector_pass", "stage_a_pass", "stage_b_pass",
        "stage_c_pass", "num_ff_conversations", "num_female_chars", "num_unknown_chars"
    ]
    t2_clean = tier2_df.drop(
        columns=[c for c in det_cols if c != "cornell_id" and c in tier2_df.columns],
        errors="ignore",
    )
    merged = pd.merge(t2_clean, df_det[det_cols], on="cornell_id")

    # False Positives: Detector=1, Crowd=0
    fps = merged[(merged["detector_pass"] == 1) & (merged["pass"] == 0)].copy()

    # False Negatives: Detector=0, Crowd=1
    fns = merged[(merged["detector_pass"] == 0) & (merged["pass"] == 1)].copy()

    def explain_fp(row):
        r = row["bechdel_rating"]
        reasons = []
        if r == 2:
            reasons.append("Crowd labeled 2 (talked only about a man): pronoun/vocab list missed contextual male reference")
        elif r == 1:
            reasons.append("Crowd labeled 1 (women do not talk): detector matched F-F conversation not credited by crowd or character misgendered")
        elif r == 0:
            reasons.append("Crowd labeled 0 (<2 women): crowd considered characters unnamed or minor, while script credited them")
        else:
            reasons.append(f"Crowd label was {r}")
        return "; ".join(reasons)

    def explain_fn(row):
        reasons = []
        if not row["stage_a_pass"]:
            if row["num_unknown_chars"] > 0:
                reasons.append(f"Stage A failed: only {row['num_female_chars']} confirmed female chars ({row['num_unknown_chars']} marked '?' in Cornell)")
            else:
                reasons.append(f"Stage A failed: only {row['num_female_chars']} female characters in script corpus")
        elif not row["stage_b_pass"]:
            reasons.append("Stage B failed: Cornell dialogue transcript omits passing scene or characters speak to group")
        elif not row["stage_c_pass"]:
            reasons.append("Stage C failed: all F-F conversations exceeded male-talk threshold (mentioned male character names/pronouns)")
        else:
            reasons.append("Multi-stage boundary condition")
        return "; ".join(reasons)

    fps["error_type"] = "False Positive (Detector=Pass, Crowd=Fail)"
    fps["primary_reason"] = fps.apply(explain_fp, axis=1)

    fns["error_type"] = "False Negative (Detector=Fail, Crowd=Pass)"
    fns["primary_reason"] = fns.apply(explain_fn, axis=1)

    top_fps = fps.head(20)
    top_fns = fns.head(20)

    combined_errors = pd.concat([top_fps, top_fns], ignore_index=True)

    export_cols = [
        "error_type", "cornell_id", "title_cornell", "year", "bechdel_rating",
        "pass", "detector_pass", "num_female_chars", "num_unknown_chars",
        "num_ff_conversations", "primary_reason"
    ]
    export_df = combined_errors[[c for c in export_cols if c in combined_errors.columns]]

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    export_df.to_csv(output_path, index=False)
    logger.info(f"Saved {len(export_df)} error analysis cases to {output_path}")

    return {
        "false_positives": top_fps,
        "false_negatives": top_fns,
        "export_df": export_df,
    }
