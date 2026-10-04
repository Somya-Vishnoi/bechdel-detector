"""Feature extraction, dialogue feature aggregation, and preprocessing pipelines."""

from bechdel.features.dialogue_features import extract_dialogue_features_for_corpus
from bechdel.features.builder import (
    build_tier1_features,
    build_tier2_features,
    get_metadata_feature_names,
    get_dialogue_feature_names,
    create_preprocessor,
)

__all__ = [
    "extract_dialogue_features_for_corpus",
    "build_tier1_features",
    "build_tier2_features",
    "get_metadata_feature_names",
    "get_dialogue_feature_names",
    "create_preprocessor",
]
