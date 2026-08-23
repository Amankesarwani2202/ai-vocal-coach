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
from utils.state import clear_user_data, init_session_state, get_voice_profile, is_level_0_complete, update_user_name
from utils.pages_config import get_level_progress, get_page_info, get_pages_by_level

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
    total_exercises = sum(item["total"] for item in progress.values())
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

        level_names = {
            0: "Diagnostics", 1: "Fundamentals", 2: "Pitch & Scales",
            3: "Articulation", 4: "Legato", 5: "Rhythm",
            6: "Resonance", 7: "Classical Technique", 8: "Repertoire I",
            9: "Repertoire II",
        }
        for row_start in range(0, 10, 2):
            columns = st.columns(2)
            for column, level in zip(columns, range(row_start, min(row_start + 2, 10))):
                with column:
                    item = progress[level]
                    st.markdown(f"**Level {level} — {level_names[level]}** &nbsp; {item['completed']}/{item['total']}")
                    st.progress(item["percentage"] / 100)

        st.divider()

        level_columns = st.columns(3)

        def ex_list(num_str, name, completed_set):
            done = any(ex_id for ex_id in completed_set if num_str in str(ex_id))
            marker = "·" if done else " "
            style = "" if done else "color:var(--text-muted,#6B6560)"
            return f"<div style='padding:0.2rem 0;font-size:0.88rem;{style}'>{marker} {name}</div>"

        for column, level in zip(level_columns, range(10)):
            with column:
                pages = get_pages_by_level(level)
                st.markdown(f"<div class='section-label'>Level {level} · {level_names[level]}</div>", unsafe_allow_html=True)
                listing = "".join(
                    ex_list(key.split("_Exercise_")[-1].split("_", 1)[0], info["title"], completed)
                    for key, info in sorted(pages.items(), key=lambda entry: entry[1].get("order", 0))
                )
                st.markdown(listing, unsafe_allow_html=True)

        st.divider()

        if progress[0]["percentage"] < 100:
            st.markdown("**Next step:** Complete Level 0 — Diagnostics to unlock personalised coaching.")
        elif progress[1]["percentage"] < 100:
            st.markdown(f"**Continue Level 1** — you've completed {progress[1]['completed']} of {progress[1]['total']} exercises.")
        elif placement_level >= 2 and progress[2]["percentage"] < 100:
            st.markdown("**Level 2 is unlocked.** Work on your pitch and scales to keep improving.")
        elif next((level for level in range(3, 10) if progress[level]["percentage"] < 100), None) is not None:
            next_level = next(level for level in range(3, 10) if progress[level]["percentage"] < 100)
            st.markdown(f"**Continue Level {next_level}** — keep building your technique and musicality.")
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
        df = pd.DataFrame(st.session_state.history).copy()
        df["exercise"] = df["exercise"].map(
            lambda key: get_page_info(key).get(
                "title",
                str(key).split("_Exercise_")[-1].replace("_", " "),
            )
        )
        visible_columns = [column for column in ["timestamp", "exercise", "score", "xp"] if column in df]
        st.dataframe(
            df[visible_columns],
            width="stretch",
            hide_index=True,
            column_config={
                "exercise": st.column_config.TextColumn("Exercise", width="large"),
                "score": st.column_config.NumberColumn(format="%.0f/100"),
                "timestamp": st.column_config.TextColumn(width="medium"),
            },
        )
    else:
        st.caption("No sessions recorded yet. Complete an exercise to start tracking.")

    st.divider()
    with st.expander("Start as a new user"):
        st.caption("This clears your name, scores, history, and vocal profile for this session.")
        confirm_clear = st.checkbox("I understand this cannot be undone", key="confirm_clear_data")
        if st.button("Clear data and restart", disabled=not confirm_clear, key="clear_user_data"):
            clear_user_data()
            st.rerun()
