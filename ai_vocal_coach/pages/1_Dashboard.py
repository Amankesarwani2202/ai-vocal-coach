from pathlib import Path
import sys

import pandas as pd
import streamlit as st
import numpy as np

ROOT = Path(__file__).resolve().parent
if ROOT.name == "pages":
    ROOT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from components.ui import display_header, inject_custom_css, render_theme_toggle, render_top_nav
from utils.state import init_session_state, get_voice_profile, is_level_0_complete, update_user_name
from utils.pages_config import get_level_progress, get_pages_by_level

init_session_state()
inject_custom_css()

if not st.session_state.get("user_name"):
    # Welcome / onboarding screen
    render_top_nav("home")

    st.markdown("""
    <div style="max-width:480px;margin:4rem auto 0 auto;text-align:center">
        <h1 style="font-size:2.2rem;font-weight:700;letter-spacing:-0.02em;margin-bottom:0.4rem">
            Train your voice
        </h1>
        <p style="color:var(--text-muted,#6B6560);font-size:1rem;line-height:1.6;margin-bottom:2rem">
            Personalised exercises that listen to you sing and give real feedback.
            No music theory required — just your voice and 10 minutes a day.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col_pad1, col_input, col_pad2 = st.columns([1, 2, 1])
    with col_input:
        name_value = st.text_input(
            "What should we call you?",
            placeholder="Your first name",
            key="welcome_name_input",
            label_visibility="visible",
        )

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        if st.button("Get started", use_container_width=True, key="welcome_continue"):
            if name_value.strip():
                update_user_name(name_value.strip())
            else:
                update_user_name("Guest")
            st.rerun()

        st.markdown("""
        <p style="text-align:center;font-size:0.78rem;color:var(--text-muted,#6B6560);margin-top:1rem">
            Takes about 20 minutes to complete your initial assessment.
            <br>You can pause and come back any time.
        </p>
        """, unsafe_allow_html=True)

else:
    # Main dashboard
    display_header("Your Progress", "", show_profile_editor=False)

    level_0_complete = is_level_0_complete()
    voice_profile = get_voice_profile() if level_0_complete else {}
    completed = st.session_state.completed_exercises
    progress = get_level_progress(completed)

    col1, col2, col3 = st.columns(3)
    col1.metric("XP", f"{st.session_state.xp}")
    col2.metric("Exercises completed", len(completed))
    total_exercises = 15
    completion_pct = int((len(completed) / total_exercises * 100) if total_exercises > 0 else 0)
    col3.metric("Overall", f"{completion_pct}%", f"{len(completed)}/{total_exercises}")

    st.divider()

    if level_0_complete:
        st.markdown("<div class='section-label'>Your vocal profile</div>", unsafe_allow_html=True)

        pvcol1, pvcol2, pvcol3, pvcol4 = st.columns(4)
        pvcol1.metric("Range", f"{voice_profile.get('range_low_note', '—')} – {voice_profile.get('range_high_note', '—')}")
        pvcol2.metric("Voice type", voice_profile.get("voice_type", "Unknown"))
        pvcol3.metric("Level placement", f"Level {voice_profile.get('placement_level', 1)}")

        weak_areas = voice_profile.get("weak_areas", [])
        weak_str = ", ".join(weak_areas[:2]) if weak_areas else "None identified"
        if len(weak_areas) > 2:
            weak_str += f" +{len(weak_areas) - 2}"
        pvcol4.metric("Focus areas", weak_str)

        st.divider()

        st.markdown("<div class='section-label'>Level progression</div>", unsafe_allow_html=True)

        prog_col1, prog_col2 = st.columns(2)

        with prog_col1:
            st.markdown(f"**Level 0 — Diagnostics** &nbsp; {progress[0]['completed']}/{progress[0]['total']}")
            st.progress(progress[0]["percentage"] / 100)
            st.markdown(f"**Level 1 — Fundamentals** &nbsp; {progress[1]['completed']}/{progress[1]['total']}")
            st.progress(progress[1]["percentage"] / 100)

        with prog_col2:
            placement_level = voice_profile.get("placement_level", 1)
            if placement_level >= 2:
                st.markdown(f"**Level 2 — Pitch & Scales** &nbsp; {progress[2]['completed']}/{progress[2]['total']}")
                st.progress(progress[2]["percentage"] / 100)
            else:
                st.markdown("**Level 2 — Pitch & Scales** &nbsp; Locked")
                st.caption("Complete Level 1 to unlock.")

        st.divider()

        col_l0, col_l1, col_l2 = st.columns(3)

        def ex_list(num_str, name, completed_set):
            done = any(ex_id for ex_id in completed_set if num_str in str(ex_id))
            marker = "·" if done else " "
            style = "" if done else "color:var(--text-muted,#6B6560)"
            return f"<div style='padding:0.2rem 0;font-size:0.88rem;{style}'>{marker} {name}</div>"

        with col_l0:
            st.markdown("<div class='section-label'>Diagnostics</div>", unsafe_allow_html=True)
            st.markdown(
                ex_list("0.1", "Vocal Warm-Up", completed) +
                ex_list("0.2", "Range Finder", completed) +
                ex_list("0.3", "Ear Training", completed),
                unsafe_allow_html=True,
            )

        with col_l1:
            st.markdown("<div class='section-label'>Fundamentals</div>", unsafe_allow_html=True)
            st.markdown(
                ex_list("1.1", "Diaphragmatic Support", completed) +
                ex_list("1.2", "Silent Breath", completed) +
                ex_list("1.3", "Smooth Onset", completed) +
                ex_list("1.4", "Legato", completed) +
                ex_list("1.5", "Five-Note Scale", completed) +
                ex_list("1.6", "Staccato vs Legato", completed),
                unsafe_allow_html=True,
            )

        with col_l2:
            st.markdown("<div class='section-label'>Pitch & Scales</div>", unsafe_allow_html=True)
            locked_style = "" if placement_level >= 2 else "opacity:0.4"
            st.markdown(f"<div style='{locked_style}'>", unsafe_allow_html=True)
            st.markdown(
                ex_list("2.1", "Major Scale Ascending", completed) +
                ex_list("2.2", "Major Scale Descending", completed) +
                ex_list("2.3", "Minor Scales", completed) +
                ex_list("2.4", "Interval Training", completed) +
                ex_list("2.5", "Arpeggios", completed) +
                ex_list("2.6", "Pitch Stability", completed),
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

        st.divider()

        if progress[0]["percentage"] < 100:
            st.markdown("**Next step:** Complete Level 0 — Diagnostics to unlock personalised coaching.")
        elif progress[1]["percentage"] < 100:
            st.markdown(f"**Continue Level 1** — you've completed {progress[1]['completed']} of {progress[1]['total']} exercises.")
        elif placement_level >= 2 and progress[2]["percentage"] < 100:
            st.markdown("**Level 2 is unlocked.** Work on your pitch and scales to keep improving.")
        else:
            st.markdown("All exercises complete. Keep practising to improve your scores.")

    else:
        user_name = st.session_state.get("user_name", "")
        greeting = f"Hi {user_name}. " if user_name and user_name != "Guest" else ""

        st.markdown(
            f"{greeting}Your first step is a short vocal assessment — three exercises that "
            "take around 20 minutes. This builds your vocal profile and unlocks "
            "personalised coaching for everything that follows."
        )

        st.markdown("")

        if st.button("Start your assessment", key="cta_start_assessment"):
            st.switch_page("pages/2a_Exercise_0.1_Warm_Up.py")

        st.divider()

        st.markdown("<div class='section-label'>How it works</div>", unsafe_allow_html=True)

        cols = st.columns(3)

        with cols[0]:
            st.markdown("**Assessment**")
            st.markdown("3 quick exercises to understand your voice — range, pitch matching, and breath.")

        with cols[1]:
            st.markdown("**Fundamentals**")
            st.markdown("6 exercises on breath support, tone quality, and smooth note connections.")

        with cols[2]:
            st.markdown("**Pitch & Scales**")
            st.markdown("6 exercises on scales, intervals, and pitch stability.")

        st.divider()

        st.markdown("<div class='section-label'>Tips for accurate feedback</div>", unsafe_allow_html=True)
        st.markdown("""
- Find a quiet room — background noise reduces feedback accuracy
- Sing at a comfortable volume, close to your microphone
- Sustain notes for at least 1–2 seconds when asked
- Use open vowels (ah, oh, eh) unless told otherwise
        """)

    st.divider()

    st.markdown("<div class='section-label'>Recent activity</div>", unsafe_allow_html=True)

    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(
            df,
            width="stretch",
            hide_index=True,
            column_config={
                "score": st.column_config.NumberColumn(format="%.0f/100"),
                "timestamp": st.column_config.TextColumn(width="medium"),
            },
        )
    else:
        st.caption("No sessions recorded yet. Complete an exercise to start tracking.")
