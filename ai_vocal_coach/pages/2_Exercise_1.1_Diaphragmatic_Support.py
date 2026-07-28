import streamlit as st
from utils.state import init_session_state, add_score
from utils.file_handler import temp_audio_file
from components.ui import display_header, render_score_badge, inject_custom_css
from analysis.audio_processor import AudioProcessor
from engine.feedback import evaluate_diaphragmatic_support
from visualization.charts import plot_waveform, plot_radar_score

init_session_state()
inject_custom_css()

display_header("Exercise 1.1: Diaphragmatic Support Basics", "Master your breath control.")

st.markdown("""
**Instructions:**
1. Inhale silently from your diaphragm.
2. Sustain a continuous "sss" or "zzz" sound.
3. Keep the volume and airflow as steady as possible.
""")

audio_val = st.audio_input("Record your exercise (aim for 5-10 seconds)")

if audio_val:
    with st.spinner("Analyzing acoustics..."):
        try:
            with temp_audio_file(audio_val) as temp_path:
                processor = AudioProcessor(temp_path)
                score, feedback, subscores = evaluate_diaphragmatic_support(processor)
                
            st.markdown(f"### Score: {render_score_badge(score)}", unsafe_allow_html=True)
            
            st.subheader("AI Feedback")
            for f in feedback:
                st.write(f)
                
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(plot_radar_score(subscores), use_container_width=True)
            with col2:
                st.plotly_chart(plot_waveform(processor.y, processor.sr), use_container_width=True)
            
            if st.button("Claim XP & Save Score"):
                add_score("Exercise 1.1", score, xp_earned=50)
                st.success("Progress saved! You earned 50 XP.")
                
        except Exception as e:
            st.error(f"Error processing audio: {e}. Please try a longer recording.")