from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
if ROOT.name == "pages":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.state import init_session_state, add_score
from utils.file_handler import temp_audio_file
from components.ui import display_header, render_score_badge
from analysis.audio_processor import AudioProcessor
from engine.feedback import evaluate_generic
from visualization.charts import plot_pitch_contour

init_session_state()
display_header("Exercise 1.4: Legato Connection", "Connect notes seamlessly.")

st.markdown("**Instructions:** Sing a gentle 'Do-Re-Mi-Re-Do' scale. Keep the airflow continuous.")
audio_val = st.audio_input("Record your Legato phrase")

if audio_val:
    with st.spinner("Tracking pitch continuity..."):
        with temp_audio_file(audio_val) as temp_path:
            processor = AudioProcessor(temp_path)
            score, feedback, _ = evaluate_generic(processor, "legato")
            times, pitches = processor.get_pitch_contour()
            
        st.markdown(f"### Score: {render_score_badge(score)}", unsafe_allow_html=True)
        st.plotly_chart(plot_pitch_contour(times, pitches), use_container_width=True)
        if st.button("Claim XP"): add_score("Exercise 1.4", score, 50); st.success("Saved!")