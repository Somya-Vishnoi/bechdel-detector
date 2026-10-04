"""Tests for Stage A, Stage B, and Stage C dialogue detector rules."""

import pandas as pd
import pytest
from bechdel.detector.rules import DialogueDetector


@pytest.fixture
def detector():
    return DialogueDetector(male_talk_threshold=0.03)


def test_scenario_1_fewer_than_two_women(detector):
    """Film with only 1 female character must fail Stage A."""
    chars = pd.DataFrame([
        {"char_id": "u0", "char_name": "SARAH", "gender": "f"},
        {"char_id": "u1", "char_name": "JOHN", "gender": "m"},
    ])
    lines_map = {"L1": "Hello Sarah.", "L2": "Hello John."}
    convs = pd.DataFrame([
        {"conv_id": "c1", "char1_id": "u0", "char2_id": "u1", "line_ids": ["L1", "L2"]}
    ])

    res = detector.analyze_film("m1", "Film 1", chars, lines_map, convs)
    assert res["stage_a_pass"] is False
    assert res["stage_b_pass"] is False
    assert res["stage_c_pass"] is False
    assert res["detector_pass"] is False


def test_scenario_2_two_women_no_conversation(detector):
    """Film with 2 female characters who do not speak to each other passes Stage A but fails Stage B."""
    chars = pd.DataFrame([
        {"char_id": "u0", "char_name": "SARAH", "gender": "f"},
        {"char_id": "u1", "char_name": "JOHN", "gender": "m"},
        {"char_id": "u2", "char_name": "MARY", "gender": "f"},
    ])
    lines_map = {"L1": "Hello Sarah.", "L2": "Hello John."}
    convs = pd.DataFrame([
        {"conv_id": "c1", "char1_id": "u0", "char2_id": "u1", "line_ids": ["L1", "L2"]}
    ])

    res = detector.analyze_film("m2", "Film 2", chars, lines_map, convs)
    assert res["stage_a_pass"] is True
    assert res["stage_b_pass"] is False
    assert res["stage_c_pass"] is False
    assert res["detector_pass"] is False


def test_scenario_3_two_women_talk_only_about_men(detector):
    """Two women talk, but the conversation is solely about a male character (Bob, he, him)."""
    chars = pd.DataFrame([
        {"char_id": "u0", "char_name": "SARAH", "gender": "f"},
        {"char_id": "u1", "char_name": "BOB", "gender": "m"},
        {"char_id": "u2", "char_name": "MARY", "gender": "f"},
    ])
    lines_map = {
        "L1": "Do you love Bob? He is my boyfriend and my husband.",
        "L2": "Yes, Bob is a handsome man. I love him too.",
    }
    convs = pd.DataFrame([
        {"conv_id": "c1", "char1_id": "u0", "char2_id": "u2", "line_ids": ["L1", "L2"]}
    ])

    res = detector.analyze_film("m3", "Film 3", chars, lines_map, convs, threshold=0.03)
    assert res["stage_a_pass"] is True
    assert res["stage_b_pass"] is True
    assert res["stage_c_pass"] is False  # Flagged about man
    assert res["detector_pass"] is False


def test_scenario_4_two_women_talk_about_science(detector):
    """Two women talk about physics and space -> Passes Stage A, B, and C."""
    chars = pd.DataFrame([
        {"char_id": "u0", "char_name": "SARAH", "gender": "f"},
        {"char_id": "u1", "char_name": "BOB", "gender": "m"},
        {"char_id": "u2", "char_name": "MARY", "gender": "f"},
    ])
    lines_map = {
        "L1": "The quantum mechanics experiment yielded unexpected results today.",
        "L2": "We should recalibrate the particle detector and review the laboratory data immediately.",
    }
    convs = pd.DataFrame([
        {"conv_id": "c1", "char1_id": "u0", "char2_id": "u2", "line_ids": ["L1", "L2"]}
    ])

    res = detector.analyze_film("m4", "Film 4", chars, lines_map, convs, threshold=0.03)
    assert res["stage_a_pass"] is True
    assert res["stage_b_pass"] is True
    assert res["stage_c_pass"] is True
    assert res["detector_pass"] is True
