"""Tests for Cornell corpus parsing with hand-made synthetic fixture files."""

import pytest
from bechdel.data.cornell_parser import (
    parse_movie_titles,
    parse_movie_characters,
    parse_movie_lines,
    parse_movie_conversations,
)


@pytest.fixture
def synthetic_corpus_dir(tmp_path):
    """Create tiny hand-made Cornell-format text files."""
    titles_file = tmp_path / "movie_titles_metadata.txt"
    titles_file.write_text(
        "m0 +++$+++ 10 things i hate about you +++$+++ 1999 +++$+++ 6.90 +++$+++ 62847 +++$+++ ['comedy', 'romance']\n"
        "m1 +++$+++ 1492: conquest of paradise +++$+++ 1992 +++$+++ 6.20 +++$+++ 10421 +++$+++ ['adventure', 'biography', 'drama']\n",
        encoding="iso-8859-1"
    )

    chars_file = tmp_path / "movie_characters_metadata.txt"
    chars_file.write_text(
        "u0 +++$+++ BIANCA +++$+++ m0 +++$+++ 10 things i hate about you +++$+++ f +++$+++ 4\n"
        "u1 +++$+++ CAMERON +++$+++ m0 +++$+++ 10 things i hate about you +++$+++ m +++$+++ 3\n"
        "u2 +++$+++ KAT +++$+++ m0 +++$+++ 10 things i hate about you +++$+++ f +++$+++ 2\n"
        "u3 +++$+++ EXTRA +++$+++ m0 +++$+++ 10 things i hate about you +++$+++ ? +++$+++ 9\n",
        encoding="iso-8859-1"
    )

    lines_file = tmp_path / "movie_lines.txt"
    lines_file.write_text(
        "L1 +++$+++ u0 +++$+++ m0 +++$+++ BIANCA +++$+++ Hi Kat.\n"
        "L2 +++$+++ u2 +++$+++ m0 +++$+++ KAT +++$+++ What are you doing?\n",
        encoding="iso-8859-1"
    )

    convs_file = tmp_path / "movie_conversations.txt"
    convs_file.write_text(
        "u0 +++$+++ u2 +++$+++ m0 +++$+++ ['L1', 'L2']\n",
        encoding="iso-8859-1"
    )

    return {
        "titles": titles_file,
        "characters": chars_file,
        "lines": lines_file,
        "conversations": convs_file,
    }


def test_parse_movie_titles(synthetic_corpus_dir):
    df = parse_movie_titles(synthetic_corpus_dir["titles"])
    assert len(df) == 2
    assert "cornell_id" in df.columns
    assert df.iloc[0]["cornell_id"] == "m0"
    assert df.iloc[0]["year"] == 1999
    assert df.iloc[0]["imdb_rating"] == 6.90
    assert "comedy" in df.iloc[0]["genres"]


def test_parse_movie_characters(synthetic_corpus_dir):
    df = parse_movie_characters(synthetic_corpus_dir["characters"])
    assert len(df) == 4
    assert df.iloc[0]["gender"] == "f"
    assert df.iloc[1]["gender"] == "m"
    assert df.iloc[3]["gender"] == "?"


def test_parse_movie_lines(synthetic_corpus_dir):
    df = parse_movie_lines(synthetic_corpus_dir["lines"])
    assert len(df) == 2
    assert df.iloc[0]["text"] == "Hi Kat."


def test_parse_movie_conversations(synthetic_corpus_dir):
    df = parse_movie_conversations(synthetic_corpus_dir["conversations"])
    assert len(df) == 1
    assert df.iloc[0]["char1_id"] == "u0"
    assert df.iloc[0]["char2_id"] == "u2"
    assert df.iloc[0]["line_ids"] == ["L1", "L2"]
