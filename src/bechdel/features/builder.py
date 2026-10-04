"""Feature set assembly, genre one-hotting, and zero-leakage preprocessing pipelines."""

import logging
from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from bechdel.data.tmdb_client import TMDBClient

logger = logging.getLogger(__name__)

TOP_GENRES = [
    "action", "adventure", "animation", "biography", "comedy", "crime",
    "drama", "fantasy", "horror", "mystery", "romance", "sci-fi", "thriller"
]


def build_tier1_features(
    bechdel_df: pd.DataFrame, tmdb_client: Optional[TMDBClient] = None
) -> pd.DataFrame:
    """Build Tier 1 feature set based on Bechdel dataset and optional TMDB enrichment."""
    df = bechdel_df.copy()
    df["year"] = pd.to_numeric(df["year"], errors="coerce")
    df["decade"] = (df["year"] // 10) * 10
    df["pass"] = (df["rating"] == 3).astype(int)

    # Add TMDB attributes if client active
    if tmdb_client and tmdb_client.is_available:
        logger.info("Enriching Tier 1 films with TMDB metadata...")
        runtimes = []
        budgets = []
        female_cast_shares = []
        director_female = []
        writer_female = []
        languages = []

        for imdb in df["imdbid"]:
            meta = tmdb_client.get_movie_metadata(imdb) if imdb else None
            if meta:
                runtimes.append(meta.get("runtime"))
                budgets.append(meta.get("budget"))
                female_cast_shares.append(meta.get("female_cast_share"))
                director_female.append(meta.get("director_female_presence"))
                writer_female.append(meta.get("writer_female_share"))
                languages.append(meta.get("original_language"))
            else:
                runtimes.append(None)
                budgets.append(None)
                female_cast_shares.append(None)
                director_female.append(None)
                writer_female.append(None)
                languages.append(None)

        df["runtime"] = runtimes
        df["budget"] = budgets
        df["female_cast_share"] = female_cast_shares
        df["director_female_presence"] = director_female
        df["writer_female_share"] = writer_female
        df["language"] = languages

    return df


def build_tier2_features(
    tier2_matched_df: pd.DataFrame,
    dialogue_features_df: pd.DataFrame,
    tmdb_client: Optional[TMDBClient] = None,
) -> pd.DataFrame:
    """Combine Tier 2 metadata and dialogue features into a unified dataset."""
    df = pd.merge(tier2_matched_df, dialogue_features_df, on="cornell_id")

    # Clean year and decade
    df["year"] = df["year_cornell"].fillna(df["year_bechdel"]).astype(int)
    df["decade"] = (df["year"] // 10) * 10

    # Clean IMDb metrics
    df["imdb_rating"] = pd.to_numeric(df["imdb_rating"], errors="coerce")
    df["imdb_votes"] = pd.to_numeric(df["imdb_votes"], errors="coerce")
    df["log_imdb_votes"] = np.log1p(df["imdb_votes"].fillna(0))

    # Parse and one-hot encode genres
    for g in TOP_GENRES:
        df[f"genre_{g}"] = df["genres"].apply(
            lambda glist: int(any(g in str(x).lower() for x in glist)) if isinstance(glist, (list, np.ndarray, tuple)) else 0
        )

    # Primary genre column for stratification or slicing
    def get_primary_genre(glist):
        if isinstance(glist, (list, np.ndarray, tuple)) and len(glist) > 0:
            for g in TOP_GENRES:
                if any(g in str(x).lower() for x in glist):
                    return g
            return str(glist[0]).lower().strip()
        return "other"

    df["primary_genre"] = df["genres"].apply(get_primary_genre)

    # TMDB enrichment if available
    if tmdb_client and tmdb_client.is_available:
        runtimes = []
        budgets = []
        director_female = []
        writer_female = []
        languages = []

        for imdb in df["imdbid"]:
            meta = tmdb_client.get_movie_metadata(imdb) if imdb else None
            if meta:
                runtimes.append(meta.get("runtime"))
                budgets.append(meta.get("budget"))
                director_female.append(meta.get("director_female_presence"))
                writer_female.append(meta.get("writer_female_share"))
                languages.append(meta.get("original_language"))
            else:
                runtimes.append(None)
                budgets.append(None)
                director_female.append(None)
                writer_female.append(None)
                languages.append(None)

        df["runtime"] = runtimes
        df["budget"] = budgets
        df["director_female_presence"] = director_female
        df["writer_female_share"] = writer_female
        df["language"] = languages

    logger.info(f"Built Tier 2 unified dataset with shape {df.shape}")
    return df


def get_metadata_feature_names() -> List[str]:
    """Features available strictly from metadata without dialogue parsing."""
    cols = ["year", "decade", "imdb_rating", "log_imdb_votes", "female_char_share"]
    cols += [f"genre_{g}" for g in TOP_GENRES]
    return cols


def get_dialogue_feature_names() -> List[str]:
    """Features derived from Cornell dialogue and character metadata."""
    return [
        "female_line_share",
        "num_ff_conversations",
        "ff_conversation_share",
        "share_ff_lines_mentioning_men",
        "longest_ff_exchange",
        "avg_male_talk_score_ff",
        "detector_stage_a",
        "detector_stage_b",
        "detector_stage_c",
        "detector_pred",
        "num_female_chars",
        "num_male_chars",
        "total_conversations",
    ]


def create_preprocessor(
    numeric_features: List[str],
    categorical_features: Optional[List[str]] = None,
) -> ColumnTransformer:
    """Create a scikit-learn ColumnTransformer for zero-leakage pipeline preprocessing.

    Fits imputation and scaling strictly inside each CV fold.
    """
    transformers = []

    if numeric_features:
        num_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ])
        transformers.append(("num", num_pipeline, numeric_features))

    if categorical_features:
        cat_pipeline = Pipeline([
            ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ])
        transformers.append(("cat", cat_pipeline, categorical_features))

    return ColumnTransformer(transformers=transformers, remainder="drop")
