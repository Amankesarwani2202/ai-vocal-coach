"""
Exercise 0.3 — Ear Training Baseline
3-round pitch-matching cycle:
  For each round: listen to reference tone → sing to match → see per-round result
  Final screen: aggregate score + save/continue
"""

import numpy as np
import streamlit as st
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent
if ROOT.name == "pages":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import inject_custom_css, render_top_nav, generate_tone
from components.exercise_flow import (
    init_exercise_flow,
    reset_for_new_exercise,
    render_stage_indicator,
    render_introduction_stage,
    reset_exercise_flow,
)
from engine.audio_analysis import analyze_pitch_match
from utils.state import init_session_state, add_score
from utils.pages_config import get_page_info

EXERCISE_ID = "2c_Exercise_0.3_Ear_Training"
NEXT_PAGE = "pages/3_Exercise_1.1_Diaphragmatic_Support.py"

# Mid-range note names used when generating random targets.
_NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

_QUALITY_META = {
    "excellent": ("Excellent match",        "score-good"),
    "good":      ("Good match",             "score-ok"),
    "fair":      ("Close — keep working",   "score-ok"),
    "off":       ("Needs more work",        "score-low"),
    "miss":      ("Far off pitch",          "score-low"),
    "no_pitch":  ("No pitch detected",      "score-low"),
    "too_short": ("Recording too short",    "score-low"),
    "no_audio":  ("No audio",               "score-low"),
}


# ─────────────────────────────────────────────
# State helpers
# ─────────────────────────────────────────────

def _init_et_state():
    if not st.session_state.get("et_initialized"):
        st.session_state.et_round   = 1
        st.session_state.et_inner   = "listen"
        st.session_state.et_results = []
        midi_notes = np.random.choice(np.arange(60, 72), size=3, replace=False)
        st.session_state.et_rounds = [
            {
                "round": index + 1,
                "note": f"{_NOTE_NAMES[midi % 12]}{midi // 12 - 1}",
                "hz": 440.0 * (2.0 ** ((int(midi) - 69) / 12.0)),
            }
            for index, midi in enumerate(midi_notes)
        ]
        st.session_state.et_initialized = True


def _reset_et_state():
    st.session_state.et_initialized = False
    st.session_state.et_round   = 1
    st.session_state.et_inner   = "listen"
    st.session_state.et_results = []


def _rounds():
    return st.session_state.get("et_rounds", [])


# ─────────────────────────────────────────────
# Shared sub-components
# ─────────────────────────────────────────────

def _round_header(rnd, total, note):
    st.markdown(
        f'<div class="round-progress-header">'
        f'<span class="round-label">Round {rnd} of {total}</span>'
        f'<span class="round-note-chip">{note}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _round_dots(current, total=3):
    dots = ""
    for i in range(1, total + 1):
        if i < current:
            cls = "round-dot done"
        elif i == current:
            cls = "round-dot active"
        else:
            cls = "round-dot"
        dots += f'<span class="{cls}"></span>'
    st.markdown(
        f'<div class="round-dots">{dots}</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Round sub-stages
# ─────────────────────────────────────────────

def _listen_stage(round_info):
    rnd, note, hz = round_info["round"], round_info["note"], round_info["hz"]
    _round_header(rnd, len(_rounds()), note)
    _round_dots(rnd)

    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-label">Reference note</div>
        <div class="round-card-note">{note}</div>
        <div class="round-card-hz">{hz:.1f} Hz</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Listen to the tone, then sing to match it.**")
    tone_bytes = generate_tone(hz, duration=2.5)
    st.audio(tone_bytes, format="audio/wav", autoplay=False)
    st.caption("Play as many times as you need before singing.")

    st.markdown("")
    if st.button("I'm ready to sing →", key=f"et_ready_{rnd}"):
        st.session_state.et_inner = "record"
        st.rerun()


def _record_stage(round_info):
    rnd, note, hz = round_info["round"], round_info["note"], round_info["hz"]
    _round_header(rnd, len(_rounds()), note)
    _round_dots(rnd)

    st.markdown(f"**Sing 'ah' and match: {note} ({hz:.0f} Hz)**")
    st.caption("Hold steadily for 2–3 seconds, then press stop.")

    audio_input = st.audio_input(
        "Record",
        key=f"et_rec_{rnd}",
        label_visibility="hidden",
    )

    col_back, col_go = st.columns(2)
    with col_back:
        if st.button("← Listen again", key=f"et_relisten_{rnd}", use_container_width=True):
            st.session_state.et_inner = "listen"
            st.rerun()

    if audio_input is not None:
        audio_bytes = audio_input.read()
        with col_go:
            if st.button("Analyse →", key=f"et_analyse_{rnd}", use_container_width=True):
                with st.spinner("Analysing pitch…"):
                    result = analyze_pitch_match(audio_bytes, hz)
                st.session_state.et_results.append({
                    "round": rnd,
                    "note":  note,
                    "hz":    hz,
                    **result,
                })
                st.session_state.et_inner = "result"
                st.rerun()


def _result_stage(round_info):
    rnd, note = round_info["round"], round_info["note"]
    _round_header(rnd, len(_rounds()), note)
    _round_dots(rnd)

    result = next(
        (r for r in st.session_state.et_results if r["round"] == rnd),
        None,
    )

    if result:
        quality   = result.get("quality", "no_audio")
        label, score_cls = _QUALITY_META.get(quality, ("—", "score-ok"))
        score     = result.get("score", 0)
        cents     = result.get("cents_deviation")
        sung_hz   = result.get("sung_hz")

        if cents is not None:
            if cents > 2:
                direction = f"+{cents:.0f}¢ sharp"
            elif cents < -2:
                direction = f"{cents:.0f}¢ flat"
            else:
                direction = "spot on"
        else:
            direction = ""

        hz_line = (
            f'<div class="pitch-sung-hz">'
            f'You sang ~{sung_hz:.0f} Hz &nbsp;·&nbsp; target {round_info["hz"]:.0f} Hz'
            f'</div>'
            if sung_hz else ""
        )

        st.markdown(f"""
        <div class="round-card pitch-result-card">
            <div class="round-result-row">
                <span style="font-size:2rem;font-weight:700">{score}</span>
                <span style="font-size:1rem;color:var(--text-muted,#6B6560)">/100</span>
            </div>
            <div class="round-result-label {score_cls}">{label}</div>
            {'<div class="pitch-deviation">' + direction + '</div>' if direction else ''}
            {hz_line}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("")
    is_last = (rnd == len(_rounds()))

    if is_last:
        if st.button("See final results →", key=f"et_finish_{rnd}"):
            st.session_state.exercise_stage = "results"
            st.rerun()
    else:
        col_next, col_retry = st.columns(2)
        with col_next:
            if st.button(f"Next round →", key=f"et_next_{rnd}", use_container_width=True):
                st.session_state.et_round = rnd + 1
                st.session_state.et_inner = "listen"
                st.rerun()
        with col_retry:
            if st.button("Try again", key=f"et_retry_{rnd}", use_container_width=True):
                st.session_state.et_results = [
                    r for r in st.session_state.et_results if r["round"] != rnd
                ]
                st.session_state.et_inner = "listen"
                st.rerun()


# ─────────────────────────────────────────────
# Recording stage dispatcher
# ─────────────────────────────────────────────

def _render_exercise_stage():
    _init_et_state()
    rnd        = st.session_state.et_round
    inner      = st.session_state.et_inner
    round_info = _rounds()[rnd - 1]

    if inner == "listen":
        _listen_stage(round_info)
    elif inner == "record":
        _record_stage(round_info)
    elif inner == "result":
        _result_stage(round_info)


# ─────────────────────────────────────────────
# Summary / results stage
# ─────────────────────────────────────────────

def _render_summary_stage():
    results = st.session_state.get("et_results", [])

    if results:
        scores  = [r.get("score", 0) for r in results]
        overall = int(np.mean(scores))
        xp      = (150 if overall >= 90
                   else 120 if overall >= 80
                   else 100 if overall >= 70
                   else 80  if overall >= 60
                   else 50)

        if overall >= 85:
            score_label, score_cls = "Excellent", "score-good"
        elif overall >= 70:
            score_label, score_cls = "Good",      "score-ok"
        else:
            score_label, score_cls = "Keep practising", "score-low"

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"""
            <div style="margin-bottom:0.25rem">
                <span style="font-size:2rem;font-weight:700;letter-spacing:-0.02em">{overall}</span>
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

        st.divider()
        st.markdown("**Round results**")

        rows_html = ""
        for r in results:
            quality = r.get("quality", "no_audio")
            label, score_cls = _QUALITY_META.get(quality, ("—", "score-ok"))
            score   = r.get("score", 0)
            cents   = r.get("cents_deviation")
            if cents is not None:
                direction = (
                    f"+{cents:.0f}¢ sharp" if cents > 2
                    else f"{cents:.0f}¢ flat" if cents < -2
                    else "spot on"
                )
            else:
                direction = "—"

            rows_html += f"""
            <div class="et-summary-row">
                <span class="et-round-note">{r['note']}</span>
                <span class="et-round-score {score_cls}">{score}/100</span>
                <span class="et-round-quality">{label}</span>
                <span class="et-round-cents">{direction}</span>
            </div>"""

        st.markdown(rows_html, unsafe_allow_html=True)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key="et_summary_retry"):
            _reset_et_state()
            st.session_state.exercise_stage = "recording"
            st.rerun()
    with col_b:
        if st.button("Save and continue", use_container_width=True, key="et_save"):
            if results:
                scores  = [r.get("score", 0) for r in results]
                overall = int(np.mean(scores))
                xp      = (150 if overall >= 90
                           else 120 if overall >= 80
                           else 100 if overall >= 70
                           else 80  if overall >= 60
                           else 50)
                add_score(EXERCISE_ID, overall, xp)
            _reset_et_state()
            reset_exercise_flow()
            st.switch_page(NEXT_PAGE)


# ─────────────────────────────────────────────
# Page entry point
# ─────────────────────────────────────────────

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
    _render_summary_stage()
