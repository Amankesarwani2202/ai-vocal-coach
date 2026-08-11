import uuid
from datetime import datetime

import streamlit as st


def init_session_state():
    """Initializes global session state variables for progress tracking."""
    if "xp" not in st.session_state:
        st.session_state.xp = 0
    if "completed_exercises" not in st.session_state:
        st.session_state.completed_exercises = set()
    if "history" not in st.session_state:
        st.session_state.history = []
    if "best_scores" not in st.session_state:
        st.session_state.best_scores = {}
    if "user_name" not in st.session_state:
        st.session_state.user_name = ""
    if "session_id" not in st.session_state:
        st.session_state.session_id = uuid.uuid4().hex[:8]
    if "session_started_at" not in st.session_state:
        st.session_state.session_started_at = datetime.now().strftime("%Y-%m-%d %H:%M")
    if "theme" not in st.session_state:
        st.session_state.theme = "light"
    if "voice_profile" not in st.session_state:
        st.session_state.voice_profile = {
            "range_low_hz": None,
            "range_high_hz": None,
            "range_low_note": None,
            "range_high_note": None,
            "voice_type": None,
            "tessitura_start_hz": None,
            "tessitura_end_hz": None,
            "placement_level": 1,
            "weak_areas": [],
            "level_0_complete": False,
        }


def update_user_name(name: str):
    """Persist the current user's display name for the session."""
    cleaned_name = (name or "").strip() or "Guest"
    st.session_state.user_name = cleaned_name
    return cleaned_name


def get_user_profile():
    """Return the current user profile data for UI rendering."""
    return {
        "name": st.session_state.user_name or "Guest",
        "session_id": st.session_state.session_id,
        "session_started_at": st.session_state.session_started_at,
    }


def add_score(exercise_id: str, score: int, xp_earned: int):
    """Updates user progress after an exercise."""
    st.session_state.xp += xp_earned
    st.session_state.completed_exercises.add(exercise_id)

    if exercise_id not in st.session_state.best_scores or score > st.session_state.best_scores[exercise_id]:
        st.session_state.best_scores[exercise_id] = score

    st.session_state.history.append(
        {
            "exercise": exercise_id,
            "score": score,
            "xp": xp_earned,
        }
    )


def update_voice_profile(profile_data: dict):
    """Updates voice profile from Level 0 diagnostics."""
    st.session_state.voice_profile.update(profile_data)


def get_voice_profile():
    """Returns current voice profile."""
    return st.session_state.voice_profile


def is_level_0_complete():
    """Check if Level 0 (diagnostics) has been completed."""
    return st.session_state.voice_profile.get("level_0_complete", False)


def toggle_theme():
    """Toggle between light and dark theme."""
    st.session_state.theme = "light" if st.session_state.theme == "dark" else "dark"


def get_current_theme():
    """Get current theme setting."""
    return st.session_state.get("theme", "light")