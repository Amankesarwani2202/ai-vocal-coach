import streamlit as st
from utils.state import init_session_state
import pandas as pd

st.set_page_config(page_title="Dashboard", layout="wide")
init_session_state()

st.title("📊 Your Progress")

col1, col2, col3 = st.columns(3)
col1.metric("Current XP", f"{st.session_state.xp} XP")
col2.metric("Exercises Conquered", len(st.session_state.completed_exercises))
avg_score = 0
if st.session_state.best_scores:
    avg_score = sum(st.session_state.best_scores.values()) / len(st.session_state.best_scores)
col3.metric("Avg Best Score", f"{int(avg_score)} / 100")

st.divider()

if st.session_state.history:
    st.subheader("Recent Activity")
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df, use_container_width=True)
else:
    st.info("You haven't completed any exercises yet. Go to Exercise 1.1 to start!")