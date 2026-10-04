"""Title normalization and fuzzy year matching between Cornell and Bechdel datasets."""

import logging
from pathlib import Path
import re
from typing import Dict, List, Optional, Tuple
import unicodedata
import pandas as pd

logger = logging.getLogger(__name__)

STOP_ARTICLES = {"the", "a", "an"}


def normalize_title(title: Optional[str]) -> str:
    """Normalize a movie title for robust cross-dataset matching."""
    if not title or not isinstance(title, str):
        return ""

    # Transliterate unicode characters to ascii (e.g. Léon -> Leon)
    text = unicodedata.normalize("NFKD", title.strip().lower()).encode("ascii", "ignore").decode("utf-8")

    # Handle inverted articles like "Godfather, The" or "Big Lebowski, The"
    for art in [", the", ", a", ", an"]:
        if text.endswith(art):
            text = art.replace(",", "").strip() + " " + text[:-len(art)].strip()

    # Remove non-alphanumeric characters
    text = re.sub(r"[^a-z0-9]+", " ", text).strip()

    tokens = text.split()
    if not tokens:
        return ""

    # Strip leading article if present
    if tokens[0] in STOP_ARTICLES and len(tokens) > 1:
        tokens = tokens[1:]

    # Strip trailing article if present
    if tokens and tokens[-1] in STOP_ARTICLES and len(tokens) > 1:
        tokens = tokens[:-1]

    return " ".join(tokens)


def match_cornell_to_bechdel(
    cornell_titles_df: pd.DataFrame,
    bechdel_df: pd.DataFrame,
    year_tolerance: int = 1,
    data_loss_path: str = "reports/data_loss.md",
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Join Cornell movies to Bechdel dataset by normalized title and year.

    Args:
        cornell_titles_df: DataFrame of Cornell titles
        bechdel_df: DataFrame of Bechdel movies (Tier 1)
        year_tolerance: Maximum absolute year difference (default ±1)
        data_loss_path: Markdown file to record data loss and join accounting

    Returns:
        (tier1_df, tier2_matched_df)
    """
    b_df = bechdel_df.copy()
    b_df["norm_title"] = b_df["title"].apply(normalize_title)

    c_df = cornell_titles_df.copy()
    c_df["norm_title"] = c_df["title"].apply(normalize_title)

    matched_rows = []
    dropped_cornell = []

    # Map Bechdel movies by normalized title for fast lookup
    bechdel_by_title: Dict[str, List[dict]] = {}
    for row in b_df.to_dict(orient="records"):
        t = row["norm_title"]
        if t:
            bechdel_by_title.setdefault(t, []).append(row)

    matched_bechdel_ids = set()

    for c_row in c_df.to_dict(orient="records"):
        c_title = c_row["norm_title"]
        c_year = c_row["year"]

        if not c_title:
            dropped_cornell.append({
                "cornell_id": c_row.get("cornell_id"),
                "title": c_row.get("title"),
                "year": c_year,
                "reason": "Empty normalized title"
            })
            continue

        candidates = bechdel_by_title.get(c_title, [])
        if not candidates:
            dropped_cornell.append({
                "cornell_id": c_row.get("cornell_id"),
                "title": c_row.get("title"),
                "year": c_year,
                "reason": "Title not found in Bechdel database"
            })
            continue

        # Check year tolerance
        year_matches = []
        for cand in candidates:
            b_year = cand["year"]
            if c_year is None or b_year is None:
                # If year unknown, allow title match
                diff = 0
            else:
                diff = abs(c_year - b_year)

            if diff <= year_tolerance:
                year_matches.append((diff, cand))

        if not year_matches:
            cand_years = [c["year"] for c in candidates]
            dropped_cornell.append({
                "cornell_id": c_row.get("cornell_id"),
                "title": c_row.get("title"),
                "year": c_year,
                "reason": f"Year mismatch with candidates {cand_years} (diff > {year_tolerance})"
            })
            continue

        # Sort by smallest year difference
        year_matches.sort(key=lambda x: x[0])
        best_diff, best_match = year_matches[0]

        matched_bechdel_ids.add(best_match["id"])
        matched_rows.append({
            "cornell_id": c_row["cornell_id"],
            "bechdel_id": best_match["id"],
            "title_cornell": c_row["title"],
            "title_bechdel": best_match["title"],
            "norm_title": c_title,
            "year_cornell": c_year,
            "year_bechdel": best_match["year"],
            "year_diff": best_diff,
            "bechdel_rating": best_match["rating"],
            "pass": best_match["pass"],
            "imdbid": best_match["imdbid"],
            "imdb_rating": c_row.get("imdb_rating"),
            "imdb_votes": c_row.get("imdb_votes"),
            "genres": c_row.get("genres", []),
        })

    tier2_df = pd.DataFrame(matched_rows)
    dropped_df = pd.DataFrame(dropped_cornell)

    total_cornell = len(c_df)
    total_bechdel = len(b_df)
    total_matched = len(tier2_df)
    total_dropped = len(dropped_df)

    logger.info(
        f"Matching complete: {total_matched}/{total_cornell} Cornell films matched to Bechdel "
        f"({(total_matched/total_cornell)*100:.1f}% match rate)."
    )

    # Write data loss accounting report
    data_loss_file = Path(data_loss_path)
    data_loss_file.parent.mkdir(parents=True, exist_ok=True)

    with open(data_loss_file, "w", encoding="utf-8") as f:
        f.write("# Data Loss & Matching Accounting Report\n\n")
        f.write(f"- **Tier 1 (Total Bechdel Films)**: {total_bechdel}\n")
        f.write(f"- **Total Cornell Films in Corpus**: {total_cornell}\n")
        f.write(f"- **Tier 2 (Successfully Matched Films)**: {total_matched}\n")
        f.write(f"- **Dropped Cornell Films**: {total_dropped}\n")
        f.write(f"- **Match Rate on Cornell**: {(total_matched/total_cornell)*100:.2f}%\n")
        f.write(f"- **Year Tolerance**: ±{year_tolerance} year(s)\n\n")

        f.write("## Summary of Drop Reasons (Cornell Films)\n\n")
        if not dropped_df.empty:
            reason_counts = dropped_df["reason"].apply(lambda r: r.split("(")[0].strip()).value_counts()
            for reason, cnt in reason_counts.items():
                f.write(f"- **{reason}**: {cnt} films\n")
        f.write("\n")

        f.write("## Tier 2 Matched Sample (First 15 Matches)\n\n")
        f.write("| Cornell ID | Bechdel ID | Title (Cornell) | Year (C / B) | Rating | Pass |\n")
        f.write("| --- | --- | --- | --- | --- | --- |\n")
        for r in tier2_df.head(15).to_dict(orient="records"):
            f.write(f"| {r['cornell_id']} | {r['bechdel_id']} | {r['title_cornell']} | {r['year_cornell']} / {r['year_bechdel']} | {r['bechdel_rating']} | {r['pass']} |\n")

        f.write("\n## Complete Log of Dropped Cornell Films\n\n")
        f.write("| Cornell ID | Title | Year | Drop Reason |\n")
        f.write("| --- | --- | --- | --- |\n")
        for r in dropped_df.to_dict(orient="records"):
            f.write(f"| {r['cornell_id']} | {r['title']} | {r['year']} | {r['reason']} |\n")

    logger.info(f"Data loss report saved to {data_loss_file}")
    return b_df, tier2_df
