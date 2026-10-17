"""Opt-in per-browser progress persistence, safe on ephemeral Streamlit hosts."""
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components
from utils.progress_store import snapshot,validate
_bridge=components.declare_component('vocal_progress_storage',path=str(Path(__file__).parent/'progress_storage'))


def sync_browser_progress():
    ready=st.session_state.get('_browser_progress_loaded',False)
    response=_bridge(data=snapshot(st.session_state),enabled=st.session_state.get('remember_progress',False),ready=ready,key='browser_progress_bridge',default=None)
    if response and response.get('unavailable'):st.session_state['_browser_progress_unavailable']=True
    if response and response.get('loaded') and not ready:
        st.session_state['_browser_progress_loaded']=True
        st.session_state['_browser_progress_unavailable']=response.get('unavailable',False)
        data=response.get('data')
        if data:
            try:
                clean=validate(data)
                if clean.get('remember_progress'):st.session_state.update(clean)
            except ValueError:st.session_state['_browser_progress_unavailable']=True
        st.rerun()
