"""Bechdel dataset ingestion and caching."""

import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional
import urllib.request
import urllib.error
import pandas as pd

logger = logging.getLogger(__name__)


def fetch_json_with_headers(url: str, timeout: int = 25) -> Any:
    """Fetch JSON from a URL with custom user-agent."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        content = resp.read().decode("utf-8")
        return json.loads(content)


def load_bechdel_data(
    raw_path: str = "data/raw/bechdel_movies.json",
    primary_url: str = "http://bechdeltest.com/api/v1/getAllMovies",
    archive_fallback_url: str = "https://web.archive.org/web/20241201000000id_/http://bechdeltest.com/api/v1/getAllMovies",
    index_fallback_url: str = "https://bechdeltest.com/search/index.json",
    force_download: bool = False,
) -> pd.DataFrame:
    """Load Bechdel test movies dataset, downloading and caching if needed.

    Tries primary API first. If HTTP 410 Gone or connection error occurs,
    automatically falls back to the authentic Wayback Machine archive snapshot,
    or the live search/index.json endpoint.

    Returns:
        pd.DataFrame with columns ['imdbid', 'title', 'year', 'rating', 'id']
    """
    raw_file = Path(raw_path)
    raw_file.parent.mkdir(parents=True, exist_ok=True)

    if raw_file.exists() and not force_download:
        logger.info(f"Loading cached Bechdel data from {raw_file}")
        with open(raw_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        return clean_bechdel_dataframe(df)

    data = None
    # 1. Try primary endpoint
    try:
        logger.info(f"Attempting download from primary Bechdel API: {primary_url}")
        data = fetch_json_with_headers(primary_url)
        logger.info(f"Successfully fetched {len(data)} records from primary API.")
    except urllib.error.HTTPError as e:
        logger.warning(f"Primary Bechdel endpoint returned HTTP {e.code} ({e.reason}). Falling back...")
    except Exception as e:
        logger.warning(f"Primary Bechdel download failed: {e}. Falling back...")

    # 2. Try archive snapshot
    if not data:
        try:
            logger.info(f"Attempting download from archive snapshot: {archive_fallback_url}")
            data = fetch_json_with_headers(archive_fallback_url)
            logger.info(f"Successfully fetched {len(data)} records from archive snapshot.")
        except Exception as e:
            logger.warning(f"Archive fallback failed: {e}. Falling back to search index...")

    # 3. Try live search index fallback
    if not data:
        try:
            logger.info(f"Attempting download from live index: {index_fallback_url}")
            raw_index = fetch_json_with_headers(index_fallback_url)
            # Format: [[id, title, year, rating, dubious], ...]
            data = [
                {
                    "id": item[0],
                    "title": item[1],
                    "year": item[2],
                    "rating": item[3],
                    "imdbid": "",
                }
                for item in raw_index
            ]
            logger.info(f"Successfully converted {len(data)} records from search/index.json.")
        except Exception as e:
            logger.error(f"Index fallback failed: {e}")

    if not data:
        msg = (
            "CRITICAL: Failed to download Bechdel Test dataset from all endpoints.\n"
            "MANUAL DOWNLOAD INSTRUCTIONS:\n"
            "1. Download the JSON from https://web.archive.org/web/20241201000000id_/http://bechdeltest.com/api/v1/getAllMovies\n"
            f"2. Save the raw JSON file to '{raw_path}'\n"
            "3. Rerun the command."
        )
        raise RuntimeError(msg)

    # Cache to disk
    with open(raw_file, "w", encoding="utf-8") as f:
        json.dump(data, f)
    logger.info(f"Cached {len(data)} Bechdel records to {raw_file}")

    df = pd.DataFrame(data)
    return clean_bechdel_dataframe(df)


def clean_bechdel_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Validate and clean Bechdel dataframe columns and datatypes."""
    required = ["id", "title", "year", "rating"]
    for col in required:
        if col not in df.columns:
            raise ValueError(f"Bechdel dataset missing required column: {col}")

    if "imdbid" not in df.columns:
        df["imdbid"] = ""

    df["id"] = pd.to_numeric(df["id"], errors="coerce").fillna(0).astype(int)
    df["year"] = pd.to_numeric(df["year"], errors="coerce").fillna(0).astype(int)
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype(int)
    df["title"] = df["title"].astype(str).str.strip()
    df["imdbid"] = df["imdbid"].astype(str).str.strip()

    # Filter out invalid years / ratings
    df = df[(df["year"] > 1870) & (df["year"] <= 2030)].copy()
    df = df[df["rating"].isin([0, 1, 2, 3])].copy()

    # Create decade and binary pass target (rating == 3)
    df["decade"] = (df["year"] // 10) * 10
    df["pass"] = (df["rating"] == 3).astype(int)
    return df.reset_index(drop=True)
