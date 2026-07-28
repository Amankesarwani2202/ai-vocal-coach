import streamlit as st
from utils.state import init_session_state, add_score
from utils.file_handler import temp_audio_file
from components.ui import display_header, render_score_badge
from analysis.audio_processor import AudioProcessor
from engine.feedback import evaluate_generic
from visualization.charts import plot_waveform

init_session_state()
display_header("Exercise 1.6: Staccato vs Legato", "Master articulation contrast.")

st.markdown("**Instructions:** Sing 3 short notes (Staccato), followed by a smooth phrase (Legato).")
audio_val = st.audio_input("Record your articulation exercise")

if audio_val:
    with st.spinner("Analyzing articulation timing..."):
        with temp_audio_file(audio_val) as temp_path:
            processor = AudioProcessor(temp_path)
            score, feedback, _ = evaluate_generic(processor, "articulation")
            
        st.markdown(f"### Score: {render_score_badge(score)}", unsafe_allow_html=True)
        st.plotly_chart(plot_waveform(processor.y, processor.sr), use_container_width=True)
        if st.button("Claim XP"): add_score("Exercise 1.6", score, 70); st.success("Saved!")