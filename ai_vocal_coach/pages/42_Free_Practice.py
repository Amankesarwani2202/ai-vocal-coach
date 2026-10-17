import streamlit as st
from utils.state import init_session_state
from components.ui import inject_custom_css
init_session_state()
inject_custom_css()
st.title('Free practice')
st.write('Sing anything you enjoy. Record, listen back and choose your own focus.')
audio=st.audio_input('Record your practice')
if audio:
    st.audio(audio)
    st.download_button('Keep this recording',audio.getvalue(),'vocal-coach-practice.wav','audio/wav')
from pathlib import Path
st.page_link(str(Path(__file__).resolve().parent/'1_Dashboard.py'),label='Back to exercises')
