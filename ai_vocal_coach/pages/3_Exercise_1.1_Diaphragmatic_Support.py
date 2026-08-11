import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if ROOT.name == "pages":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import inject_custom_css, render_top_nav
from components.exercise_flow import (
    init_exercise_flow,
    reset_for_new_exercise,
    render_stage_indicator,
    render_introduction_stage,
    render_recording_stage,
    render_results_stage,
    reset_exercise_flow,
)
from utils.state import init_session_state
from utils.pages_config import get_page_info

EXERCISE_ID = "3_Exercise_1.1_Diaphragmatic_Support"
NEXT_PAGE = "pages/4_Exercise_1.2_Silent_Breath.py"

init_session_state()
inject_custom_css()
render_top_nav("exercise")

exercise_info = get_page_info(EXERCISE_ID)

if not exercise_info:
    st.error(f"Exercise {EXERCISE_ID} not found.")
    st.stop()

init_exercise_flow()
reset_for_new_exercise(EXERCISE_ID)
render_stage_indicator(st.session_state.exercise_stage)

if st.session_state.exercise_stage == "introduction":
    render_introduction_stage(exercise_info)

elif st.session_state.exercise_stage == "recording":
    render_recording_stage(EXERCISE_ID, breathing_type="support")

elif st.session_state.exercise_stage == "results":
    render_results_stage(EXERCISE_ID, NEXT_PAGE)