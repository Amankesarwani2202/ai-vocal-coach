"""
Exercise 5.1 — Singing with the Metronome
Custom metronome pattern:
  Introduction → listen to click track → record singing → analyze rhythm timing
"""

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

EXERCISE_ID = "25_Exercise_5.1_Singing_Metronome"
NEXT_PAGE = "pages/26_Exercise_5.2_Quarter_Note_Pulse.py"
BPM = 80
BARS = 4
BEATS_PER_BAR = 4


def _init_state():
    if not st.session_state.get("m51_initialized"):
        st.session_state.m51_phase       = "listen"   # listen | record | result
        st.session_state.m51_result      = None
        st.session_state.m51_initialized = True


def _reset_state():
    st.session_state.m51_initialized = False
    st.session_state.m51_phase  = "listen"
    st.session_state.m51_result = None


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
    st.markdown(f"### Listen to the click track — {BPM} BPM")
    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-note" style="font-size:2rem">♩ = {BPM}</div>
        <div class="round-card-label">{BARS} bars · {BEATS_PER_BAR}/4 time</div>
    </div>
    """, unsafe_allow_html=True)

    click_bytes = generate_click_track(bpm=BPM, bars=BARS, beats_per_bar=BEATS_PER_BAR)
    st.audio(click_bytes, format="audio/wav", autoplay=False)
    st.caption("Internalise the pulse before recording.")
    st.markdown("")
    if st.button("Ready to record →", key="m51_to_record"):
        st.session_state.m51_phase = "record"
        st.rerun()


def _record_phase():
    _phase_bar("record")
    st.markdown("### Sing along — keep the beat in your head")
    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-label">Sing 'la' on each beat</div>
        <div class="round-card-note" style="font-size:2rem">♩ = {BPM}</div>
        <div style="font-size:0.85rem;color:var(--text-muted,#6B6560);margin-top:0.4rem">
            {BARS} bars · aim for exactly one 'la' per quarter note
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Record exactly 4 bars, then press stop.")
    audio_input = st.audio_input("Record", key="m51_rec", label_visibility="hidden")

    col_back, col_go = st.columns(2)
    with col_back:
        if st.button("← Listen again", key="m51_relisten", use_container_width=True):
            st.session_state.m51_phase = "listen"
            st.rerun()

    if audio_input is not None:
        audio_bytes = audio_input.read()
        with col_go:
            if st.button("Analyse →", key="m51_analyse", use_container_width=True):
                with st.spinner("Analysing rhythm…"):
                    result = analyze_rhythm_timing(audio_bytes, bpm=BPM, beats_per_bar=BEATS_PER_BAR, total_bars=BARS)
                st.session_state.m51_result = result
                st.session_state.m51_phase  = "result"
                st.rerun()


def _result_phase():
    _phase_bar("result")
    st.markdown("### Rhythm Results")

    result = st.session_state.m51_result
    if not result:
        st.warning("No result found.")
        return

    score = result.get("score", 0)
    xp    = result.get("xp", 50)
    timing_data = result.get("timing_data", {})

    score_label, score_cls = (
        ("Excellent timing", "score-good") if score >= 85
        else ("Good timing",       "score-ok")  if score >= 70
        else ("Keep practising",   "score-low")
    )

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom:0.25rem">
            <span style="font-size:2rem;font-weight:700;letter-spacing:-0.02em">{score}</span>
            <span style="font-size:1rem;color:var(--text-muted,#6B6560)">/100</span>
        </div>
        <span class="score-badge {score_cls}">{score_label}</span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.5rem">
            <div style="font-size:1.1rem;font-weight:700">+{xp} XP</div>
            <div style="font-size:0.75rem;color:var(--text-muted,#6B6560)">earned</div>
        </div>
        """, unsafe_allow_html=True)

    avg_dev = timing_data.get("avg_deviation_ms")
    if avg_dev is not None:
        st.divider()
        st.metric("Average timing deviation", f"{avg_dev:.0f} ms", help="Lower is better. <30ms = excellent")

    subscores = result.get("subscores", {})
    if subscores:
        st.divider()
        st.markdown("**Detail**")
        for k, v in subscores.items():
            label = k.replace("_", " ").title()
            bar_pct = max(0, min(100, int(v)))
            bar_cls = "score-good" if bar_pct >= 80 else "score-ok" if bar_pct >= 60 else "score-low"
            st.markdown(f"""
            <div style="margin-bottom:0.6rem">
                <div style="display:flex;justify-content:space-between;font-size:0.85rem;margin-bottom:2px">
                    <span>{label}</span><span class="{bar_cls}">{bar_pct}</span>
                </div>
                <div style="background:var(--border-color,#E8E3DC);border-radius:4px;height:6px">
                    <div style="width:{bar_pct}%;height:6px;border-radius:4px;background:var(--accent,#8B7355)"></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key="m51_retry"):
            _reset_state()
            st.session_state.exercise_stage = "recording"
            st.rerun()
    with col_b:
        if st.button("Save and continue", use_container_width=True, key="m51_save"):
            add_score(EXERCISE_ID, score, xp)
            _reset_state()
            reset_exercise_flow()
            st.switch_page(NEXT_PAGE)
    if st.button("View progress", use_container_width=True, key="m51_progress"):
        st.switch_page("pages/1_Dashboard.py")


def _render_exercise_stage():
    _init_state()
    phase = st.session_state.m51_phase
    if phase == "listen":
        _listen_phase()
    elif phase == "record":
        _record_phase()
    elif phase == "result":
        _result_phase()


# ── Page entry point ──────────────────────────────────

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
