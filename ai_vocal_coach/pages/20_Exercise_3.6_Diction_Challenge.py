"""
Exercise 3.6 — Diction Challenge
2-phase exercise:
  Phase 1: speak the phrase clearly (recorded, used as warmup/reference)
  Phase 2: sing the phrase on a 5-note scale — analysed with diction_challenge type
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
    init_exercise_flow,
    reset_for_new_exercise,
    render_stage_indicator,
    render_introduction_stage,
    reset_exercise_flow,
)
from engine.audio_analysis import analyze_audio
from utils.state import init_session_state, add_score
from utils.pages_config import get_page_info

EXERCISE_ID = "20_Exercise_3.6_Diction_Challenge"
NEXT_PAGE = "pages/21_Exercise_4.1_Connecting_Notes.py"

PHRASE = "Mommy made me mash my M&Ms"
PHRASE_NOTE = "Sing on: C4 – D4 – E4 – F4 – G4 (one syllable per note)"


# ── State ─────────────────────────────────────────────

def _init_state():
    if not st.session_state.get("dc_initialized"):
        st.session_state.dc_phase         = "speak"   # speak | sing | result
        st.session_state.dc_speak_done    = False
        st.session_state.dc_result        = None
        st.session_state.dc_initialized   = True


def _reset_state():
    st.session_state.dc_initialized = False
    st.session_state.dc_phase       = "speak"
    st.session_state.dc_speak_done  = False
    st.session_state.dc_result      = None


# ── Phase indicators ──────────────────────────────────

def _phase_indicator(current):
    phases = [("1", "Speak"), ("2", "Sing")]
    html = '<div class="round-progress-header">'
    for num, label in phases:
        active = "active" if num == current else ("done" if num < current else "")
        html += f'<span class="round-note-chip" style="{"font-weight:700" if active == "active" else "opacity:0.5"}">{num}. {label}</span> '
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


# ── Phase 1: Speak ────────────────────────────────────

def _speak_phase():
    _phase_indicator("1")
    st.markdown("### Phase 1: Speak the phrase")
    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-label">Say clearly and deliberately</div>
        <div class="round-card-note" style="font-size:1.4rem;line-height:1.5">"{PHRASE}"</div>
        <div style="font-size:0.85rem;color:var(--text-muted,#6B6560);margin-top:0.5rem">
            Articulate each consonant — especially the M, D, and SH sounds.
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Record yourself speaking the phrase naturally, then move on to singing.")
    audio_input = st.audio_input("Speak the phrase", key="dc_speak_rec", label_visibility="visible")

    if audio_input is not None:
        st.success("Great! Now move to the singing phase.")
        if st.button("Proceed to singing →", key="dc_to_sing", use_container_width=True):
            st.session_state.dc_speak_done = True
            st.session_state.dc_phase = "sing"
            st.rerun()
    else:
        if st.session_state.dc_speak_done:
            if st.button("Proceed to singing →", key="dc_to_sing_skip", use_container_width=True):
                st.session_state.dc_phase = "sing"
                st.rerun()


# ── Phase 2: Sing ─────────────────────────────────────

def _sing_phase():
    _phase_indicator("2")
    st.markdown("### Phase 2: Sing the phrase")
    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-label">Sing on a 5-note ascending scale</div>
        <div class="round-card-note" style="font-size:1.4rem;line-height:1.5">"{PHRASE}"</div>
        <div style="font-size:0.85rem;color:var(--text-muted,#6B6560);margin-top:0.5rem">
            {PHRASE_NOTE}
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.caption("Keep the same crisp consonants as when you spoke. Hold each vowel until the next note.")
    audio_input = st.audio_input("Sing the phrase", key="dc_sing_rec", label_visibility="visible")

    col_back, col_go = st.columns(2)
    with col_back:
        if st.button("← Back to speaking", key="dc_back_speak", use_container_width=True):
            st.session_state.dc_phase = "speak"
            st.rerun()

    if audio_input is not None:
        audio_bytes = audio_input.read()
        with col_go:
            if st.button("Analyse →", key="dc_analyse", use_container_width=True):
                with st.spinner("Analysing diction…"):
                    result = analyze_audio(audio_bytes, EXERCISE_ID)
                st.session_state.dc_result = result
                st.session_state.dc_phase = "result"
                st.rerun()


# ── Result ────────────────────────────────────────────

def _result_phase():
    _phase_indicator("2")
    st.markdown("### Results")

    result = st.session_state.dc_result
    if not result:
        st.warning("No result available.")
        return

    score = result.get("score", 0)
    xp    = result.get("xp", 50)

    score_label, score_cls = (
        ("Excellent diction", "score-good") if score >= 85
        else ("Good diction",       "score-ok")  if score >= 70
        else ("Keep practising",    "score-low")
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

    subscores = result.get("subscores", {})
    if subscores:
        st.divider()
        st.markdown("**Detail**")
        for k, v in subscores.items():
            label = k.replace("_", " ").title()
            bar_pct = max(0, min(100, v))
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

    feedback = result.get("feedback", [])
    if feedback:
        st.divider()
        for fb in feedback[:3]:
            st.info(fb.get("message", ""))

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key="dc_retry"):
            _reset_state()
            st.session_state.exercise_stage = "recording"
            st.rerun()
    with col_b:
        if st.button("Save and continue", use_container_width=True, key="dc_save"):
            add_score(EXERCISE_ID, score, xp)
            _reset_state()
            reset_exercise_flow()
            st.switch_page(NEXT_PAGE)


# ── Exercise stage dispatcher ─────────────────────────

def _render_exercise_stage():
    _init_state()
    phase = st.session_state.dc_phase
    if phase == "speak":
        _speak_phase()
    elif phase == "sing":
        _sing_phase()
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
elif st.session_state.exercise_stage == "recording":
    _render_exercise_stage()
elif st.session_state.exercise_stage == "results":
    # Results are handled inline in the recording stage for this custom flow
    _render_exercise_stage()
