"""One curriculum for prompts, playback, detection, and plotted targets."""

import json
import re
from functools import lru_cache
from pathlib import Path

import numpy as np


@lru_cache(maxsize=1)
def curriculum():
    return json.loads((Path(__file__).resolve().parents[1] / "assets/curriculum.json").read_text())


def get_profile(exercise):
    value = str(exercise)
    match = re.search(r"(?<![\d.])(\d+\.\d+)(?![\d.])", value)
    code = match.group(1) if match else None
    profiles = curriculum()
    if code in profiles:
        return dict(profiles[code])
    return dict(next((p for p in profiles.values() if p["type"] == value), profiles["0.1"]))


def note_grid(profile, bpm=None):
    notes = profile.get("notes", [])
    seconds_per_beat = 60.0 / (bpm or profile["bpm"])
    boundaries = np.r_[0, np.cumsum([n["beats"] for n in notes])] * seconds_per_beat
    offsets = np.array([n["semitones"] for n in notes], dtype=float)
    return boundaries, offsets


def target_at_times(profile, times, root_hz, bpm=None):
    """Sample flat note plateaus; no interpolation across pitch changes."""
    boundaries, offsets = note_grid(profile, bpm)
    times = np.asarray(times, dtype=float)
    target = np.full(times.shape, np.nan)
    if not len(offsets):
        return target
    idx = np.searchsorted(boundaries, times, side="right") - 1
    valid = (idx >= 0) & (idx < len(offsets))
    target[valid] = root_hz * 2.0 ** (offsets[idx[valid]] / 12.0)
    return target


def beat_grid(profile, bpm=None, vocal=False):
    key = "vocal_onset_beats" if vocal else "onset_beats"
    durations = "vocal_duration_beats" if vocal else "duration_beats"
    spb = 60.0 / (bpm or profile["bpm"])
    return np.asarray(profile.get(key, []), dtype=float) * spb, np.asarray(profile.get(durations, []), dtype=float) * spb


def expected_seconds(profile, bpm=None):
    if profile.get("segments"):
        return float(profile["segments"][-1]["end"])
    if profile.get("notes"):
        return float(note_grid(profile, bpm)[0][-1])
    if profile.get("total_beats"):
        return profile["total_beats"] * 60.0 / (bpm or profile["bpm"])
    return float(profile.get("min_seconds", 1))
