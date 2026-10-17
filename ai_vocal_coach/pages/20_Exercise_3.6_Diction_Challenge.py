"""Retain the spoken recording and compare it against the sung phrase."""
from pathlib import Path
import sys
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.exercise_flow import (
    init_exercise_flow, reset_for_new_exercise, render_stage_indicator,
    render_introduction_stage, recording_input, render_recording_stage, render_results_stage,
)
from components.ui import inject_custom_css, render_top_nav
from utils.exercise_models import get_profile
from utils.pages_config import get_page_info
from utils.state import init_session_state

EXERCISE_ID = "20_Exercise_3.6_Diction_Challenge"
NEXT_PAGE = "pages/21_Exercise_4.1_Connecting_Notes.py"
PHRASE = "The morning sun shines on the mountain."

init_session_state()
inject_custom_css()
render_top_nav("exercise")
init_exercise_flow()
reset_for_new_exercise(EXERCISE_ID)
render_stage_indicator(st.session_state.exercise_stage)

if st.session_state.exercise_stage == "introduction":
    render_introduction_stage(get_page_info(EXERCISE_ID))
elif st.session_state.exercise_stage == "recording":
    if not st.session_state.get("spoken_audio_bytes"):
        st.markdown("### Phase 1 · Speak")
        st.write(PHRASE)
        st.caption("Speak naturally with defined consonants and complete word endings.")
        profile = get_profile(EXERCISE_ID)
        profile["pitch_model"] = "free"
        audio, _ = recording_input(EXERCISE_ID, profile, suffix="spoken")
        if audio and st.button("Continue to singing", key="diction_to_sing"):
            st.session_state.spoken_audio_bytes = audio
            st.rerun()
    else:
        st.markdown("### Phase 2 · Sing")
        st.write(PHRASE)
        st.caption("Sing sol-fa-mi-re-do, keeping the same clear consonants as your spoken version.")
        with st.expander("Listen to your spoken baseline"):
            st.audio(st.session_state.spoken_audio_bytes, format="audio/wav")
        render_recording_stage(EXERCISE_ID, context={"spoken_audio_bytes":st.session_state.spoken_audio_bytes})
elif st.session_state.exercise_stage == "results":
    render_results_stage(EXERCISE_ID, NEXT_PAGE)
