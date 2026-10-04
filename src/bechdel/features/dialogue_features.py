"""Dialogue feature extraction per film."""

import logging
from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from bechdel.detector.rules import DialogueDetector

logger = logging.getLogger(__name__)


def extract_dialogue_features_for_corpus(
    tier2_df: pd.DataFrame,
    cornell_data: Dict[str, pd.DataFrame],
    detector: Optional[DialogueDetector] = None,
    threshold: Optional[float] = None,
    tmdb_client: Optional[Any] = None,
) -> pd.DataFrame:
    """Extract film-level dialogue and detector features for Tier 2 films."""
    if detector is None:
        detector = DialogueDetector()

    lines_df = cornell_data["lines"]
    chars_df = cornell_data["characters"]
    convs_df = cornell_data["conversations"]

    # Pre-index lines for fast lookup
    lines_map = dict(zip(lines_df["line_id"], lines_df["text"]))

    # Count spoken lines per character
    char_line_counts = lines_df.groupby(["cornell_id", "char_id"]).size().to_dict()

    feature_rows = []

    for _, row in tier2_df.iterrows():
        c_id = row["cornell_id"]
        f_chars = chars_df[chars_df["cornell_id"] == c_id]
        f_convs = convs_df[convs_df["cornell_id"] == c_id]
        f_lines = lines_df[lines_df["cornell_id"] == c_id]

        tmdb_map = None
        if tmdb_client and tmdb_client.is_available and row.get("imdbid"):
            meta = tmdb_client.get_movie_metadata(str(row["imdbid"]))
            if meta:
                tmdb_map = meta.get("char_gender_map")

        # Analyze dialogues using detector
        det_res = detector.analyze_film(
            cornell_id=c_id,
            film_title=row.get("title_cornell", ""),
            film_chars=f_chars,
            film_lines_map=lines_map,
            film_convs=f_convs,
            threshold=threshold,
            tmdb_gender_map=tmdb_map,
        )

        # Character gender line counts
        total_lines = len(f_lines)
        female_lines = 0
        male_lines = 0
        unk_lines = 0

        for _, ch in f_chars.iterrows():
            cid = ch["char_id"]
            cg = ch["gender"]
            cnt = char_line_counts.get((c_id, cid), 0)
            if cg == "f":
                female_lines += cnt
            elif cg == "m":
                male_lines += cnt
            else:
                unk_lines += cnt

        f_line_share = (female_lines / total_lines) if total_lines > 0 else 0.0
        m_line_share = (male_lines / total_lines) if total_lines > 0 else 0.0

        n_fem = det_res["num_female_chars"]
        n_male = det_res["num_male_chars"]
        n_total_gendered = n_fem + n_male
        fem_char_share = (n_fem / n_total_gendered) if n_total_gendered > 0 else 0.0

        total_convs = det_res["total_conversations"]
        n_ff_convs = det_res["num_ff_conversations"]
        ff_conv_share = (n_ff_convs / total_convs) if total_convs > 0 else 0.0

        feature_rows.append({
            "cornell_id": c_id,
            "female_line_share": f_line_share,
            "male_line_share": m_line_share,
            "female_lines_count": female_lines,
            "total_lines_count": total_lines,
            "num_ff_conversations": n_ff_convs,
            "ff_conversation_share": ff_conv_share,
            "share_ff_lines_mentioning_men": det_res["share_ff_lines_mentioning_men"],
            "longest_ff_exchange": det_res["longest_ff_exchange"],
            "avg_male_talk_score_ff": det_res["avg_male_talk_score_ff"],
            "detector_stage_a": int(det_res["stage_a_pass"]),
            "detector_stage_b": int(det_res["stage_b_pass"]),
            "detector_stage_c": int(det_res["stage_c_pass"]),
            "detector_pred": int(det_res["detector_pass"]),
            "num_female_chars": n_fem,
            "num_male_chars": n_male,
            "num_unknown_chars": det_res["num_unknown_chars"],
            "female_char_share": fem_char_share,
            "total_conversations": total_convs,
        })

    features_df = pd.DataFrame(feature_rows)
    logger.info(f"Extracted dialogue features for {len(features_df)} films.")
    return features_df
