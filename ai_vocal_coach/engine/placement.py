import numpy as np


# Standard vocal range boundaries (Hz, based on operatic definitions)
VOICE_RANGES = {
    "soprano": {"low": 260, "high": 1050},  # C4 - C6
    "mezzo-soprano": {"low": 220, "high": 900},  # A3 - A5
    "alto": {"low": 195, "high": 800},  # G3 - G5
    "tenor": {"low": 145, "high": 600},  # D3 - D5
    "baritone": {"low": 110, "high": 500},  # A2 - C5
    "bass": {"low": 80, "high": 400},  # E2 - G4
}


def classify_voice_type(min_hz, max_hz):
    """Classify voice type based on detected range."""
    if min_hz is None or max_hz is None:
        return None

    mid_hz = (min_hz + max_hz) / 2

    for voice_type, ranges in VOICE_RANGES.items():
        if ranges["low"] <= mid_hz <= ranges["high"]:
            return voice_type

    if mid_hz > VOICE_RANGES["soprano"]["high"]:
        return "soprano"
    else:
        return "bass"


def compute_placement(level_0_results):
    """
    Compute placement level and weak areas from Level 0 diagnostics.

    Args:
        level_0_results: dict with keys "warm_up_score", "range_data", "ear_training_score"

    Returns:
        tuple: (placement_level, weak_areas_list)
    """
    weak_areas = []
    scores = []

    if "warm_up_score" in level_0_results:
        scores.append(level_0_results["warm_up_score"])
        if level_0_results["warm_up_score"] < 60:
            weak_areas.append("breath_control")
        if level_0_results.get("tone_score", 100) < 60:
            weak_areas.append("tone_quality")

    if "ear_training_score" in level_0_results:
        scores.append(level_0_results["ear_training_score"])
        if level_0_results["ear_training_score"] < 60:
            weak_areas.append("pitch_accuracy")

    avg_score = np.mean(scores) if scores else 50

    # Placement logic: start at Level 1 for all; advance to 2 if strong performance
    placement_level = 2 if avg_score >= 75 else 1

    return placement_level, weak_areas
