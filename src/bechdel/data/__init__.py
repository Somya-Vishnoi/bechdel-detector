"""Data ingestion, parsing, TMDB enrichment, and matching modules."""

from bechdel.data.bechdel_loader import load_bechdel_data
from bechdel.data.cornell_parser import parse_cornell_corpus
from bechdel.data.matching import normalize_title, match_cornell_to_bechdel
from bechdel.data.tmdb_client import TMDBClient

__all__ = [
    "load_bechdel_data",
    "parse_cornell_corpus",
    "normalize_title",
    "match_cornell_to_bechdel",
    "TMDBClient",
]
