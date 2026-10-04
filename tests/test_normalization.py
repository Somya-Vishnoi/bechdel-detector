"""Tests for title normalization and string cleaning."""

import pytest
from bechdel.data.matching import normalize_title


@pytest.mark.parametrize(
    "input_title,expected",
    [
        ("The Matrix", "matrix"),
        ("Matrix, The", "matrix"),
        ("A Beautiful Mind", "beautiful mind"),
        ("Beautiful Mind, A", "beautiful mind"),
        ("An Education", "education"),
        ("10 Things I Hate About You", "10 things i hate about you"),
        ("Star Wars: Episode IV - A New Hope", "star wars episode iv a new hope"),
        ("Léon: The Professional", "leon the professional"),
        ("  Pulp   Fiction  ", "pulp fiction"),
        ("Alien", "alien"),
        ("", ""),
        (None, ""),
    ],
)
def test_normalize_title(input_title, expected):
    assert normalize_title(input_title) == expected
