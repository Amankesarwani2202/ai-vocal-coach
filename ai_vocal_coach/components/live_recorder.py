"""Microphone capture with local visual cues and a shared metronome clock."""

import base64
from pathlib import Path

import streamlit.components.v1 as components

_recorder = components.declare_component("vocal_live_recorder", path=str(Path(__file__).parent / "recorder"))


def live_recorder(profile, key, reference_hz=None):
    result = _recorder(profile=profile, reference_hz=reference_hz, key=key, default=None)
    if not result or not result.get("wav_base64"):
        return None, {}
    try:
        data = base64.b64decode(result["wav_base64"], validate=True)
    except (ValueError, TypeError):
        return None, {}
    context = {}
    if result.get("performance_start_seconds") is not None:
        context["performance_start_seconds"] = result["performance_start_seconds"]
    return data, context
