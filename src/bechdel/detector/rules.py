"""Rule-based Bechdel Dialogue Detector."""

from dataclasses import dataclass, field
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
import numpy as np
import pandas as pd
from sklearn.metrics import f1_score

logger = logging.getLogger(__name__)

DEFAULT_MALE_PRONOUNS = {"he", "him", "his", "himself"}
DEFAULT_MALE_RELATIONS = {
    "boyfriend", "boyfriends", "husband", "husbands", "father", "fathers",
    "dad", "dads", "brother", "brothers", "son", "sons", "man", "men",
    "guy", "guys", "male", "males", "uncle", "uncles", "nephew", "nephews",
    "king", "prince", "groom", "fiance", "fiancé", "stepfather", "ex-boyfriend"
}


@dataclass
class ConversationAnalysis:
    """Detailed analysis of a single conversation."""
    film_id: str
    film_title: str
    conv_id: str
    char1_id: str
    char2_id: str
    char1_name: str
    char2_name: str
    char1_gender: str
    char2_gender: str
    is_female_female: bool
    num_lines: int
    text: str
    male_mentions: int
    total_words: int
    male_talk_score: float
    flagged_about_man: bool


class DialogueDetector:
    """Rule-based Bechdel Detector based on film character metadata and dialogue."""

    def __init__(
        self,
        male_pronouns: Optional[Set[str]] = None,
        male_relations: Optional[Set[str]] = None,
        male_talk_threshold: float = 0.03,
    ):
        self.male_pronouns = set(male_pronouns) if male_pronouns else DEFAULT_MALE_PRONOUNS
        self.male_relations = set(male_relations) if male_relations else DEFAULT_MALE_RELATIONS
        self.male_talk_threshold = male_talk_threshold

    def compute_male_talk_score(
        self, text: str, male_names: Set[str]
    ) -> Tuple[int, int, float]:
        """Compute male-talk score for a string of text.

        Returns:
            (male_mention_count, total_words, male_talk_score)
        """
        if not text:
            return 0, 0, 0.0

        # Tokenize to alphanumeric lowercase words
        tokens = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        total_words = len(tokens)
        if total_words == 0:
            return 0, 0, 0.0

        male_vocab = self.male_pronouns | self.male_relations | male_names
        mention_count = sum(1 for tok in tokens if tok in male_vocab)
        density = mention_count / total_words

        return mention_count, total_words, density

    def extract_film_male_names(self, film_chars: pd.DataFrame) -> Set[str]:
        """Extract first names of known male characters in a film."""
        male_names = set()
        male_chars = film_chars[film_chars["gender"] == "m"]
        for _, row in male_chars.iterrows():
            name = str(row["char_name"]).strip().lower()
            tokens = re.findall(r"\b[a-z]{3,}\b", name)
            if tokens:
                first = tokens[0]
                # Avoid common function words masquerading as names
                if first not in {"the", "and", "dr", "doctor", "mr", "sir", "officer", "agent"}:
                    male_names.add(first)
        return male_names

    def analyze_film(
        self,
        cornell_id: str,
        film_title: str,
        film_chars: pd.DataFrame,
        film_lines_map: Dict[str, str],
        film_convs: pd.DataFrame,
        threshold: Optional[float] = None,
        tmdb_gender_map: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Run Stages A, B, and C for a single film.

        Returns dictionary of film-level metrics and conversation analyses.
        """
        th = threshold if threshold is not None else self.male_talk_threshold

        # Stage A: Count female characters with known gender >= 2 (fill '?' via TMDB if available)
        char_dict = {}
        for _, r in film_chars.iterrows():
            cid = r["char_id"]
            cname = str(r["char_name"]).strip()
            g = r["gender"]
            if g == "?" and tmdb_gender_map:
                norm_cname = cname.lower()
                first_tok = norm_cname.split()[0] if norm_cname.split() else ""
                if norm_cname in tmdb_gender_map:
                    g = tmdb_gender_map[norm_cname]
                elif first_tok in tmdb_gender_map:
                    g = tmdb_gender_map[first_tok]

            char_dict[cid] = {"name": cname, "gender": g}

        num_f = sum(1 for c in char_dict.values() if c["gender"] == "f")
        num_m = sum(1 for c in char_dict.values() if c["gender"] == "m")
        num_unk = sum(1 for c in char_dict.values() if c["gender"] == "?")
        stage_a_pass = num_f >= 2

        male_names = self.extract_film_male_names(film_chars)

        # Stage B & C: Process conversations
        ff_conversations: List[ConversationAnalysis] = []
        all_conversations: List[ConversationAnalysis] = []

        total_ff_lines = 0
        ff_lines_mentioning_men = 0
        longest_ff_exchange = 0

        for _, c_row in film_convs.iterrows():
            c1_id = c_row["char1_id"]
            c2_id = c_row["char2_id"]
            conv_id = c_row.get("conv_id", "")
            line_ids = c_row.get("line_ids", [])

            c1_info = char_dict.get(c1_id, {"name": "UNKNOWN", "gender": "?"})
            c2_info = char_dict.get(c2_id, {"name": "UNKNOWN", "gender": "?"})

            is_ff = (c1_info["gender"] == "f" and c2_info["gender"] == "f")

            # Collect dialogue text
            lines_text = [film_lines_map.get(lid, "") for lid in line_ids]
            conv_text = " ".join([t for t in lines_text if t])

            mentions, words, score = self.compute_male_talk_score(conv_text, male_names)
            flagged = bool(score >= th)

            analysis = ConversationAnalysis(
                film_id=cornell_id,
                film_title=film_title,
                conv_id=conv_id,
                char1_id=c1_id,
                char2_id=c2_id,
                char1_name=c1_info["name"],
                char2_name=c2_info["name"],
                char1_gender=c1_info["gender"],
                char2_gender=c2_info["gender"],
                is_female_female=is_ff,
                num_lines=len(line_ids),
                text=conv_text,
                male_mentions=mentions,
                total_words=words,
                male_talk_score=score,
                flagged_about_man=flagged,
            )
            all_conversations.append(analysis)

            if is_ff:
                ff_conversations.append(analysis)
                total_ff_lines += len(line_ids)
                if len(line_ids) > longest_ff_exchange:
                    longest_ff_exchange = len(line_ids)

                for lt in lines_text:
                    m_cnt, _, _ = self.compute_male_talk_score(lt, male_names)
                    if m_cnt > 0:
                        ff_lines_mentioning_men += 1

        stage_b_pass = len(ff_conversations) > 0

        # Stage C: At least one F-F conversation is NOT about a man (score < threshold)
        if not stage_b_pass:
            stage_c_pass = False
        else:
            passing_ff_convs = [c for c in ff_conversations if not c.flagged_about_man]
            stage_c_pass = len(passing_ff_convs) > 0

        # Overall detector pass: A and B and C
        detector_pass = bool(stage_a_pass and stage_b_pass and stage_c_pass)

        # Dialogue-level summary metrics
        share_ff_lines_men = (ff_lines_mentioning_men / total_ff_lines) if total_ff_lines > 0 else 0.0
        avg_male_talk = (
            float(np.mean([c.male_talk_score for c in ff_conversations]))
            if ff_conversations else 0.0
        )

        return {
            "cornell_id": cornell_id,
            "film_title": film_title,
            "num_female_chars": num_f,
            "num_male_chars": num_m,
            "num_unknown_chars": num_unk,
            "stage_a_pass": stage_a_pass,
            "stage_b_pass": stage_b_pass,
            "stage_c_pass": stage_c_pass,
            "detector_pass": detector_pass,
            "num_ff_conversations": len(ff_conversations),
            "total_conversations": len(all_conversations),
            "total_ff_lines": total_ff_lines,
            "longest_ff_exchange": longest_ff_exchange,
            "share_ff_lines_mentioning_men": share_ff_lines_men,
            "avg_male_talk_score_ff": avg_male_talk,
            "ff_conversations": ff_conversations,
        }

    def tune_threshold_on_train(
        self,
        train_film_ids: Set[str],
        film_chars_df: pd.DataFrame,
        lines_map: Dict[str, str],
        convs_df: pd.DataFrame,
        ground_truth_map: Dict[str, int],
        threshold_candidates: Optional[List[float]] = None,
    ) -> float:
        """Find the optimal male-talk threshold ONLY on training set to maximize F1.

        Never touches test/validation data.
        """
        if threshold_candidates is None:
            threshold_candidates = [
                0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.035, 0.04, 0.05, 0.06, 0.08, 0.10
            ]

        logger.info(f"Tuning male-talk threshold on {len(train_film_ids)} training films...")
        best_th = self.male_talk_threshold
        best_f1 = -1.0

        for th in threshold_candidates:
            preds = []
            trues = []
            for fid in train_film_ids:
                if fid not in ground_truth_map:
                    continue
                f_chars = film_chars_df[film_chars_df["cornell_id"] == fid]
                f_convs = convs_df[convs_df["cornell_id"] == fid]
                analysis = self.analyze_film(
                    cornell_id=fid,
                    film_title="",
                    film_chars=f_chars,
                    film_lines_map=lines_map,
                    film_convs=f_convs,
                    threshold=th,
                )
                preds.append(int(analysis["detector_pass"]))
                trues.append(ground_truth_map[fid])

            if len(preds) > 0:
                score = f1_score(trues, preds, zero_division=0)
                if score > best_f1:
                    best_f1 = score
                    best_th = th

        logger.info(f"Optimal male-talk threshold on train split: {best_th} (Train F1: {best_f1:.4f})")
        self.male_talk_threshold = best_th
        return best_th
