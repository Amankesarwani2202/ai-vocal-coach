import streamlit as st
from utils.state import init_session_state, add_score
from utils.file_handler import temp_audio_file
from components.ui import display_header, render_score_badge
from analysis.audio_processor import AudioProcessor
from engine.feedback import evaluate_scale
from visualization.charts import plot_pitch_contour, plot_radar_score

init_session_state()
display_header("Exercise 1.5: Five Note Scale", "Pitch accuracy and stability check.")

st.markdown("**Instructions:** Sing an ascending scale: Do-Re-Mi-Fa-So.")
audio_val = st.audio_input("Record your scale")

if audio_val:
    with st.spinner("Calculating pitch accuracy..."):
        with temp_audio_file(audio_val) as temp_path:
            processor = AudioProcessor(temp_path)
            score, feedback, subscores = evaluate_scale(processor)
            times, pitches = processor.get_pitch_contour()
            
        st.markdown(f"### Score: {render_score_badge(score)}", unsafe_allow_html=True)
        for f in feedback: st.write(f)
        
        col1, col2 = st.columns(2)
        with col1: st.plotly_chart(plot_radar_score(subscores), use_container_width=True)
        with col2: st.plotly_chart(plot_pitch_contour(times, pitches), use_container_width=True)
            
        if st.button("Claim XP"): add_score("Exercise 1.5", score, 60); st.success("Saved!")