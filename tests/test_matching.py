"""Tests for cross-dataset matching logic and data loss logging."""

import pandas as pd
import pytest
from bechdel.data.matching import match_cornell_to_bechdel


def test_match_cornell_to_bechdel(tmp_path):
    cornell_df = pd.DataFrame([
        {"cornell_id": "m1", "title": "The Matrix", "year": 1999, "imdb_rating": 8.7, "imdb_votes": 100000, "genres": ["sci-fi"]},
        {"cornell_id": "m2", "title": "Alien", "year": 1979, "imdb_rating": 8.5, "imdb_votes": 80000, "genres": ["horror"]},
        {"cornell_id": "m3", "title": "Titanic", "year": 1997, "imdb_rating": 7.8, "imdb_votes": 90000, "genres": ["drama"]},
        {"cornell_id": "m4", "title": "Ghostbusters", "year": 1984, "imdb_rating": 7.8, "imdb_votes": 70000, "genres": ["comedy"]},
        {"cornell_id": "m5", "title": "Unmatched Film", "year": 2005, "imdb_rating": 5.0, "imdb_votes": 100, "genres": ["drama"]},
    ])

    bechdel_df = pd.DataFrame([
        {"id": 1, "title": "Matrix, The", "year": 1999, "rating": 3, "pass": 1, "imdbid": "0133093"},
        {"id": 2, "title": "Alien", "year": 1979, "rating": 3, "pass": 1, "imdbid": "0078748"},
        {"id": 3, "title": "Titanic", "year": 1998, "rating": 3, "pass": 1, "imdbid": "0120338"},  # Year diff = 1 (within tolerance)
        {"id": 4, "title": "Ghostbusters", "year": 2016, "rating": 3, "pass": 1, "imdbid": "1289401"},  # Year diff = 32 (exceeds tolerance)
    ])

    loss_file = tmp_path / "data_loss.md"
    t1_res, t2_res = match_cornell_to_bechdel(
        cornell_titles_df=cornell_df,
        bechdel_df=bechdel_df,
        year_tolerance=1,
        data_loss_path=str(loss_file),
    )

    # Matrix, Alien, and Titanic should match (3 matched films)
    assert len(t2_res) == 3
    matched_ids = set(t2_res["cornell_id"])
    assert "m1" in matched_ids  # The Matrix
    assert "m2" in matched_ids  # Alien
    assert "m3" in matched_ids  # Titanic (year 1997 vs 1998, diff=1 <= 1)
    assert "m4" not in matched_ids  # Ghostbusters 1984 vs 2016 (diff=32)
    assert "m5" not in matched_ids  # Unmatched Film

    assert loss_file.exists()
    content = loss_file.read_text(encoding="utf-8")
    assert "Dropped Cornell Films" in content
