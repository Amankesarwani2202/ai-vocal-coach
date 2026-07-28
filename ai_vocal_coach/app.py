from pathlib import Path
import sys

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import display_header, inject_custom_css
from utils.state import init_session_state

st.set_page_config(page_title="AI Vocal Coach", page_icon="🎤", layout="wide")
init_session_state()
inject_custom_css()

display_header(
    "📊 Your Progress",
    "Track your recent sessions, XP, and best scores.",
    show_profile_editor=True,
)

st.caption("Dashboard • Personal coaching overview")

col1, col2, col3 = st.columns(3)
col1.metric("Current XP", f"{st.session_state.xp} XP")
col2.metric("Exercises Conquered", len(st.session_state.completed_exercises))
avg_score = 0
if st.session_state.best_scores:
    avg_score = sum(st.session_state.best_scores.values()) / len(st.session_state.best_scores)
col3.metric("Avg Best Score", f"{int(avg_score)} / 100")

st.markdown("---")

if st.session_state.history:
    st.subheader("Recent Activity")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("You haven't completed any exercises yet. Go to Exercise 1.1 to start!")