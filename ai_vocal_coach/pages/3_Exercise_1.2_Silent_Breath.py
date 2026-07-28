import streamlit as st
from utils.state import init_session_state, add_score
from utils.file_handler import temp_audio_file
from components.ui import display_header, render_score_badge, inject_custom_css
from analysis.audio_processor import AudioProcessor
from engine.feedback import evaluate_generic
from visualization.charts import plot_waveform, plot_radar_score

init_session_state()
inject_custom_css()
display_header("Exercise 1.2: Silent Breath Control", "Minimize intake noise.")

st.markdown("""
**Instructions:**
1. Inhale deeply but silently.
2. Hold for a moment.
3. Release the breath slowly.
""")

audio_val = st.audio_input("Record your breathing cycle")

if audio_val:
    with st.spinner("Analyzing breath noise..."):
        with temp_audio_file(audio_val) as temp_path:
            processor = AudioProcessor(temp_path)
            score, feedback, subscores = evaluate_generic(processor, "breath")
            
        st.markdown(f"### Score: {render_score_badge(score)}", unsafe_allow_html=True)
        st.plotly_chart(plot_waveform(processor.y, processor.sr), use_container_width=True)
        
        if st.button("Claim XP & Save Score"):
            add_score("Exercise 1.2", score, xp_earned=40)
            st.success("Progress saved! You earned 40 XP.")