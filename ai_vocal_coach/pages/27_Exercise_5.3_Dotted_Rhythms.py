"""Exercise 5.3 — Dotted Rhythms"""

import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if ROOT.name == "pages":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import inject_custom_css, render_top_nav
from components.exercise_flow import (
    init_exercise_flow, reset_for_new_exercise, render_stage_indicator,
    render_introduction_stage, reset_exercise_flow,
)
from engine.audio_analysis import generate_click_track, analyze_rhythm_timing
from utils.state import init_session_state, add_score
from utils.pages_config import get_page_info

EXERCISE_ID = "27_Exercise_5.3_Dotted_Rhythms"
NEXT_PAGE = "pages/28_Exercise_5.4_Triplets.py"
BPM = 76
BARS = 4
BEATS_PER_BAR = 4


def _init_state():
    if not st.session_state.get("m53_initialized"):
        st.session_state.m53_phase       = "listen"
        st.session_state.m53_result      = None
        st.session_state.m53_initialized = True


def _reset_state():
    st.session_state.m53_initialized = False
    st.session_state.m53_phase  = "listen"
    st.session_state.m53_result = None


def _phase_bar(current):
    phases = [("Listen", "listen"), ("Record", "record"), ("Results", "result")]
    html = '<div class="round-progress-header">'
    for label, key in phases:
        active = key == current
        html += f'<span class="round-note-chip" style="{"font-weight:700" if active else "opacity:0.5"}">{label}</span> '
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def _listen_phase():
    _phase_bar("listen")
    st.markdown(f"### Listen — {BPM} BPM")
    st.caption("Dotted rhythms: long-short pattern (dotted quarter + eighth). Listen carefully.")
    click_bytes = generate_click_track(bpm=BPM, bars=BARS, beats_per_bar=BEATS_PER_BAR)
    st.audio(click_bytes, format="audio/wav", autoplay=False)
    if st.button("Ready to record →", key="m53_to_record"):
        st.session_state.m53_phase = "record"
        st.rerun()


def _record_phase():
    _phase_bar("record")
    st.markdown(f"### Sing 'la' in a dotted-quarter + eighth pattern — {BPM} BPM")
    st.caption("Long-short-long-short — feel the lilt.")
    audio_input = st.audio_input("Record", key="m53_rec", label_visibility="hidden")

    col_back, col_go = st.columns(2)
    with col_back:
        if st.button("← Listen again", key="m53_relisten", use_container_width=True):
            st.session_state.m53_phase = "listen"
            st.rerun()
    if audio_input is not None:
        audio_bytes = audio_input.read()
        with col_go:
            if st.button("Analyse →", key="m53_analyse", use_container_width=True):
                with st.spinner("Analysing…"):
                    result = analyze_rhythm_timing(audio_bytes, bpm=BPM, beats_per_bar=BEATS_PER_BAR, total_bars=BARS)
                st.session_state.m53_result = result
                st.session_state.m53_phase  = "result"
                st.rerun()


def _result_phase():
    _phase_bar("result")
    result = st.session_state.m53_result or {}
    score = result.get("score", 0)
    xp    = result.get("xp", 50)
    avg_dev = result.get("timing_data", {}).get("avg_deviation_ms")

    score_label, score_cls = (
        ("Excellent", "score-good") if score >= 85
        else ("Good", "score-ok") if score >= 70
        else ("Keep practising", "score-low")
    )
    st.markdown(f"""
    <div style="margin-bottom:0.5rem">
        <span style="font-size:2rem;font-weight:700">{score}</span>
        <span style="font-size:1rem;color:var(--text-muted,#6B6560)">/100</span>
        &nbsp;<span class="score-badge {score_cls}">{score_label}</span>
        &nbsp;<span style="font-size:1rem;font-weight:600">+{xp} XP</span>
    </div>
    """, unsafe_allow_html=True)
    if avg_dev is not None:
        st.metric("Average deviation", f"{avg_dev:.0f} ms")

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key="m53_retry"):
            _reset_state()
            st.session_state.exercise_stage = "recording"
            st.rerun()
    with col_b:
        if st.button("Save and continue", use_container_width=True, key="m53_save"):
            add_score(EXERCISE_ID, score, xp)
            _reset_state()
            reset_exercise_flow()
            st.switch_page(NEXT_PAGE)
    if st.button("View progress", use_container_width=True, key="m53_progress"):
        st.switch_page("pages/1_Dashboard.py")


def _render_exercise_stage():
    _init_state()
    phase = st.session_state.m53_phase
    if phase == "listen":   _listen_phase()
    elif phase == "record": _record_phase()
    elif phase == "result": _result_phase()


init_session_state()
inject_custom_css()
render_top_nav("exercise")
exercise_info = get_page_info(EXERCISE_ID)
if not exercise_info:
    st.error(f"Exercise {EXERCISE_ID} not found.")
    st.stop()
init_exercise_flow()
reset_for_new_exercise(EXERCISE_ID)
render_stage_indicator(st.session_state.exercise_stage)
if st.session_state.exercise_stage == "introduction":
    render_introduction_stage(exercise_info)
elif st.session_state.exercise_stage in ("recording", "results"):
    _render_exercise_stage()
