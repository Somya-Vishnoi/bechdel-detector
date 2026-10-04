"""Parser for Cornell Movie-Dialogs Corpus."""

import ast
import logging
from pathlib import Path
import shutil
from typing import Dict, List, Optional, Tuple
import urllib.request
import zipfile
import pandas as pd

logger = logging.getLogger(__name__)

CORNELL_DELIMITER = " +++$+++ "
CORNELL_ENCODING = "iso-8859-1"


def download_and_extract_cornell(
    url: str = "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip",
    zip_path: str = "data/raw/cornell_movie_dialogs_corpus.zip",
    extract_dir: str = "data/raw/cornell",
    force_download: bool = False,
) -> Path:
    """Download and extract Cornell corpus if not already extracted."""
    zip_file = Path(zip_path)
    extract_path = Path(extract_dir)

    # Check if extracted files exist
    expected_file = find_cornell_file(extract_path, "movie_titles_metadata.txt")
    if expected_file and not force_download:
        logger.info(f"Cornell corpus already extracted in {extract_path}")
        return expected_file.parent

    zip_file.parent.mkdir(parents=True, exist_ok=True)
    extract_path.mkdir(parents=True, exist_ok=True)

    if not zip_file.exists() or force_download:
        logger.info(f"Downloading Cornell corpus from {url} to {zip_file}")
        try:
            req = urllib.request.Request(
                url,
                headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)"}
            )
            with urllib.request.urlopen(req, timeout=60) as resp, open(zip_file, "wb") as out:
                shutil.copyfileobj(resp, out)
            logger.info("Download completed successfully.")
        except Exception as e:
            msg = (
                f"CRITICAL: Failed to download Cornell Movie-Dialogs Corpus from {url}.\n"
                f"Error: {e}\n"
                "MANUAL DOWNLOAD INSTRUCTIONS:\n"
                f"1. Download zip file manually from {url}\n"
                f"2. Save to '{zip_file}'\n"
                "3. Rerun the command."
            )
            raise RuntimeError(msg) from e

    logger.info(f"Extracting {zip_file} to {extract_path}")
    with zipfile.ZipFile(zip_file, "r") as z:
        z.extractall(extract_path)

    found = find_cornell_file(extract_path, "movie_titles_metadata.txt")
    if not found:
        raise FileNotFoundError(f"Could not locate movie_titles_metadata.txt inside {extract_path}")
    return found.parent


def find_cornell_file(base_dir: Path, filename: str) -> Optional[Path]:
    """Search recursively for a Cornell data file."""
    if not base_dir.exists():
        return None
    matches = list(base_dir.rglob(filename))
    return matches[0] if matches else None


def parse_movie_titles(file_path: Path) -> pd.DataFrame:
    """Parse movie_titles_metadata.txt."""
    rows = []
    with open(file_path, "r", encoding=CORNELL_ENCODING, errors="replace") as f:
        for line in f:
            parts = line.strip().split(CORNELL_DELIMITER)
            if len(parts) >= 6:
                m_id = parts[0].strip()
                title = parts[1].strip()
                year_raw = parts[2].strip()
                rating_raw = parts[3].strip()
                votes_raw = parts[4].strip()
                genres_raw = parts[5].strip()

                # Clean year: some entries have /I or formatting
                year_clean = "".join([c for c in year_raw if c.isdigit()])
                year = int(year_clean[:4]) if len(year_clean) >= 4 else None

                # Clean rating
                try:
                    rating = float(rating_raw)
                except ValueError:
                    rating = None

                # Clean votes
                try:
                    votes = int("".join([c for c in votes_raw if c.isdigit()]))
                except ValueError:
                    votes = None

                # Clean genres
                try:
                    genres = ast.literal_eval(genres_raw)
                    if not isinstance(genres, list):
                        genres = [str(genres)]
                except Exception:
                    genres = [g.strip().strip("'\"") for g in genres_raw.strip("[]").split(",") if g.strip()]

                rows.append({
                    "cornell_id": m_id,
                    "title": title,
                    "year": year,
                    "imdb_rating": rating,
                    "imdb_votes": votes,
                    "genres": genres,
                })
    df = pd.DataFrame(rows)
    return df


def parse_movie_characters(file_path: Path) -> pd.DataFrame:
    """Parse movie_characters_metadata.txt."""
    rows = []
    with open(file_path, "r", encoding=CORNELL_ENCODING, errors="replace") as f:
        for line in f:
            parts = line.strip().split(CORNELL_DELIMITER)
            if len(parts) >= 6:
                char_id = parts[0].strip()
                char_name = parts[1].strip()
                movie_id = parts[2].strip()
                movie_title = parts[3].strip()
                gender = parts[4].strip().lower()
                if gender not in ["m", "f"]:
                    gender = "?"
                credit_pos = parts[5].strip()
                try:
                    pos = int(credit_pos)
                except ValueError:
                    pos = None

                rows.append({
                    "char_id": char_id,
                    "char_name": char_name,
                    "cornell_id": movie_id,
                    "movie_title": movie_title,
                    "gender": gender,
                    "credit_pos": pos,
                })
    return pd.DataFrame(rows)


def parse_movie_lines(file_path: Path) -> pd.DataFrame:
    """Parse movie_lines.txt."""
    rows = []
    with open(file_path, "r", encoding=CORNELL_ENCODING, errors="replace") as f:
        for line in f:
            parts = line.strip().split(CORNELL_DELIMITER)
            if len(parts) >= 5:
                line_id = parts[0].strip()
                char_id = parts[1].strip()
                movie_id = parts[2].strip()
                char_name = parts[3].strip()
                text = parts[4].strip()
                rows.append({
                    "line_id": line_id,
                    "char_id": char_id,
                    "cornell_id": movie_id,
                    "char_name": char_name,
                    "text": text,
                })
    return pd.DataFrame(rows)


def parse_movie_conversations(file_path: Path) -> pd.DataFrame:
    """Parse movie_conversations.txt."""
    rows = []
    with open(file_path, "r", encoding=CORNELL_ENCODING, errors="replace") as f:
        for idx, line in enumerate(f):
            parts = line.strip().split(CORNELL_DELIMITER)
            if len(parts) >= 4:
                char1_id = parts[0].strip()
                char2_id = parts[1].strip()
                movie_id = parts[2].strip()
                lines_raw = parts[3].strip()
                try:
                    lines_list = ast.literal_eval(lines_raw)
                except Exception:
                    lines_list = [l.strip().strip("'\"") for l in lines_raw.strip("[]").split(",") if l.strip()]

                rows.append({
                    "conv_id": f"conv_{idx}",
                    "char1_id": char1_id,
                    "char2_id": char2_id,
                    "cornell_id": movie_id,
                    "line_ids": lines_list,
                })
    return pd.DataFrame(rows)


def parse_cornell_corpus(
    extract_dir: str = "data/raw/cornell",
    zip_path: str = "data/raw/cornell_movie_dialogs_corpus.zip",
    url: str = "http://www.cs.cornell.edu/~cristian/data/cornell_movie_dialogs_corpus.zip",
    force_download: bool = False,
) -> Dict[str, pd.DataFrame]:
    """Complete workflow: download/extract and parse all Cornell files into DataFrames."""
    corpus_dir = download_and_extract_cornell(
        url=url,
        zip_path=zip_path,
        extract_dir=extract_dir,
        force_download=force_download
    )

    logger.info(f"Parsing Cornell corpus from {corpus_dir}")
    titles_file = corpus_dir / "movie_titles_metadata.txt"
    chars_file = corpus_dir / "movie_characters_metadata.txt"
    lines_file = corpus_dir / "movie_lines.txt"
    convs_file = corpus_dir / "movie_conversations.txt"

    df_titles = parse_movie_titles(titles_file)
    df_chars = parse_movie_characters(chars_file)
    df_lines = parse_movie_lines(lines_file)
    df_convs = parse_movie_conversations(convs_file)

    logger.info(
        f"Parsed {len(df_titles)} titles, {len(df_chars)} characters, "
        f"{len(df_lines)} lines, {len(df_convs)} conversations."
    )

    return {
        "titles": df_titles,
        "characters": df_chars,
        "lines": df_lines,
        "conversations": df_convs,
    }
