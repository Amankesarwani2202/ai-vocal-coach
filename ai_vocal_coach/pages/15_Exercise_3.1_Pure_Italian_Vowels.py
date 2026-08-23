"""
Exercise 3.1 — Pure Italian Vowels
5-round pitch-matching cycle, one vowel per round (A E I O U).
Each round: listen to reference tone (A4 440Hz) → sing on that vowel → per-round result.
Final screen: aggregate score + save/continue.
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

EXERCISE_ID = "15_Exercise_3.1_Pure_Italian_Vowels"
NEXT_PAGE = "pages/16_Exercise_3.2_Vowel_Consistency_Ascending.py"

ROUNDS = [
    {"round": 1, "vowel": "A", "ipa": "[a]",  "hz": 440.0, "note": "A4", "tip": "Open mouth wide, tongue flat and low"},
    {"round": 2, "vowel": "E", "ipa": "[e]",  "hz": 440.0, "note": "A4", "tip": "Corners slightly spread, mid-high tongue"},
    {"round": 3, "vowel": "I", "ipa": "[i]",  "hz": 440.0, "note": "A4", "tip": "Widest smile shape, high front tongue"},
    {"round": 4, "vowel": "O", "ipa": "[o]",  "hz": 440.0, "note": "A4", "tip": "Rounded lips, back tongue raised"},
    {"round": 5, "vowel": "U", "ipa": "[u]",  "hz": 440.0, "note": "A4", "tip": "Lips forward like a tube, back tongue high"},
]

_QUALITY_META = {
    "excellent": ("Excellent match",      "score-good"),
    "good":      ("Good match",           "score-ok"),
    "fair":      ("Close — keep working", "score-ok"),
    "off":       ("Needs more work",      "score-low"),
    "miss":      ("Far off pitch",        "score-low"),
    "no_pitch":  ("No pitch detected",    "score-low"),
    "too_short": ("Recording too short",  "score-low"),
    "no_audio":  ("No audio",             "score-low"),
}


# ── State ────────────────────────────────────────────

def _init_state():
    if not st.session_state.get("vow_initialized"):
        st.session_state.vow_round       = 1
        st.session_state.vow_inner       = "listen"
        st.session_state.vow_results     = []
        st.session_state.vow_initialized = True


def _reset_state():
    st.session_state.vow_initialized = False
    st.session_state.vow_round   = 1
    st.session_state.vow_inner   = "listen"
    st.session_state.vow_results = []


# ── Shared widgets ────────────────────────────────────

def _round_header(rnd, vowel, ipa):
    st.markdown(
        f'<div class="round-progress-header">'
        f'<span class="round-label">Round {rnd} of {len(ROUNDS)}</span>'
        f'<span class="round-note-chip">Vowel {vowel} {ipa}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def _round_dots(current):
    dots = ""
    for i in range(1, len(ROUNDS) + 1):
        cls = "round-dot done" if i < current else ("round-dot active" if i == current else "round-dot")
        dots += f'<span class="{cls}"></span>'
    st.markdown(f'<div class="round-dots">{dots}</div>', unsafe_allow_html=True)


# ── Sub-stages ────────────────────────────────────────

def _listen_stage(info):
    rnd, vowel, ipa, hz, note, tip = (
        info["round"], info["vowel"], info["ipa"],
        info["hz"], info["note"], info["tip"],
    )
    _round_header(rnd, vowel, ipa)
    _round_dots(rnd)

    st.markdown(f"""
    <div class="round-card">
        <div class="round-card-label">Sing on vowel</div>
        <div class="round-card-note" style="font-size:3rem">{vowel}</div>
        <div class="round-card-hz">{note} · {hz:.0f} Hz</div>
        <div style="font-size:0.85rem;color:var(--text-muted,#6B6560);margin-top:0.5rem">{tip}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("**Listen to the reference pitch, then sing on this vowel.**")
    tone_bytes = generate_tone(hz, duration=2.5)
    st.audio(tone_bytes, format="audio/wav", autoplay=False)
    st.caption("Play as many times as needed before singing.")

    st.markdown("")
    if st.button(f"Ready to sing '{vowel}' →", key=f"vow_ready_{rnd}"):
        st.session_state.vow_inner = "record"
        st.rerun()


def _record_stage(info):
    rnd, vowel, ipa, hz = info["round"], info["vowel"], info["ipa"], info["hz"]
    _round_header(rnd, vowel, ipa)
    _round_dots(rnd)

    st.markdown(f"**Sing '{vowel}' and match: {info['note']} ({hz:.0f} Hz)**")
    st.caption("Hold the vowel steadily for 2–3 seconds, then press stop.")

    audio_input = st.audio_input("Record", key=f"vow_rec_{rnd}", label_visibility="hidden")

    col_back, col_go = st.columns(2)
    with col_back:
        if st.button("← Listen again", key=f"vow_relisten_{rnd}", use_container_width=True):
            st.session_state.vow_inner = "listen"
            st.rerun()

    if audio_input is not None:
        audio_bytes = audio_input.read()
        with col_go:
            if st.button("Analyse →", key=f"vow_analyse_{rnd}", use_container_width=True):
                with st.spinner("Analysing pitch…"):
                    result = analyze_pitch_match(audio_bytes, hz)
                st.session_state.vow_results.append({
                    "round": rnd, "vowel": vowel, "hz": hz, **result,
                })
                st.session_state.vow_inner = "result"
                st.rerun()


def _result_stage(info):
    rnd, vowel, ipa = info["round"], info["vowel"], info["ipa"]
    _round_header(rnd, vowel, ipa)
    _round_dots(rnd)

    result = next((r for r in st.session_state.vow_results if r["round"] == rnd), None)

    if result:
        quality = result.get("quality", "no_audio")
        label, score_cls = _QUALITY_META.get(quality, ("—", "score-ok"))
        score = result.get("score", 0)
        cents = result.get("cents_deviation")

        if cents is not None:
            if cents > 2:
                direction = f"+{cents:.0f}¢ sharp"
            elif cents < -2:
                direction = f"{cents:.0f}¢ flat"
            else:
                direction = "spot on"
        else:
            direction = ""

        sung_hz = result.get("sung_hz")
        hz_line = (
            f'<div class="pitch-sung-hz">You sang ~{sung_hz:.0f} Hz &nbsp;·&nbsp; target {info["hz"]:.0f} Hz</div>'
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
    is_last = (rnd == len(ROUNDS))

    if is_last:
        if st.button("See final results →", key=f"vow_finish_{rnd}"):
            st.session_state.exercise_stage = "results"
            st.rerun()
    else:
        col_next, col_retry = st.columns(2)
        with col_next:
            if st.button("Next vowel →", key=f"vow_next_{rnd}", use_container_width=True):
                st.session_state.vow_round = rnd + 1
                st.session_state.vow_inner = "listen"
                st.rerun()
        with col_retry:
            if st.button("Try again", key=f"vow_retry_{rnd}", use_container_width=True):
                st.session_state.vow_results = [r for r in st.session_state.vow_results if r["round"] != rnd]
                st.session_state.vow_inner = "listen"
                st.rerun()


# ── Exercise stage dispatcher ─────────────────────────

def _render_exercise_stage():
    _init_state()
    rnd        = st.session_state.vow_round
    inner      = st.session_state.vow_inner
    round_info = ROUNDS[rnd - 1]

    if inner == "listen":
        _listen_stage(round_info)
    elif inner == "record":
        _record_stage(round_info)
    elif inner == "result":
        _result_stage(round_info)


# ── Summary / results stage ───────────────────────────

def _render_summary_stage():
    results = st.session_state.get("vow_results", [])

    if results:
        scores  = [r.get("score", 0) for r in results]
        overall = int(np.mean(scores))
        xp      = (150 if overall >= 90 else 120 if overall >= 80
                   else 100 if overall >= 70 else 80 if overall >= 60 else 50)

        score_label, score_cls = (
            ("Excellent", "score-good") if overall >= 85
            else ("Good", "score-ok") if overall >= 70
            else ("Keep practising", "score-low")
        )

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
        st.markdown("**Vowel results**")

        rows_html = ""
        for r in results:
            quality = r.get("quality", "no_audio")
            label, score_cls = _QUALITY_META.get(quality, ("—", "score-ok"))
            score = r.get("score", 0)
            cents = r.get("cents_deviation")
            direction = (
                f"+{cents:.0f}¢ sharp" if cents is not None and cents > 2
                else f"{cents:.0f}¢ flat" if cents is not None and cents < -2
                else "spot on" if cents is not None
                else "—"
            )
            rows_html += f"""
            <div class="et-summary-row">
                <span class="et-round-note" style="font-size:1.2rem;font-weight:700">{r['vowel']}</span>
                <span class="et-round-score {score_cls}">{score}/100</span>
                <span class="et-round-quality">{label}</span>
                <span class="et-round-cents">{direction}</span>
            </div>"""
        st.markdown(rows_html, unsafe_allow_html=True)

    st.divider()
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key="vow_summary_retry"):
            _reset_state()
            st.session_state.exercise_stage = "recording"
            st.rerun()
    with col_b:
        if st.button("Save and continue", use_container_width=True, key="vow_save"):
            if results:
                scores  = [r.get("score", 0) for r in results]
                overall = int(np.mean(scores))
                xp      = (150 if overall >= 90 else 120 if overall >= 80
                           else 100 if overall >= 70 else 80 if overall >= 60 else 50)
                add_score(EXERCISE_ID, overall, xp)
            _reset_state()
            reset_exercise_flow()
            st.switch_page(NEXT_PAGE)


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
    _render_summary_stage()
