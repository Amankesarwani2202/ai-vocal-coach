import streamlit as st
from utils.state import init_session_state
from components.ui import inject_custom_css

st.set_page_config(page_title="AI Vocal Coach", page_icon="🎤", layout="wide")
init_session_state()
inject_custom_css()

st.title("🎤 AI Vocal Coach")
st.markdown("""
Welcome to your personal AI vocal coach. 
We focus on **Level 1: Foundational Technique**. 
Navigate using the sidebar to track your dashboard or start your exercises.
""")

st.info("👈 Select an exercise from the sidebar to begin training!")

# Quick stats summary on landing
cols = st.columns(3)
cols[0].metric("Total XP", st.session_state.xp)
cols[1].metric("Exercises Completed", len(st.session_state.completed_exercises))