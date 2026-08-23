"""
Sidebar Component
"""

import streamlit as st
from utils.pages_config import (
    get_pages_by_level,
    get_level_progress,
    is_page_unlocked,
    get_level_badge,
)
from utils.state import is_level_0_complete, get_voice_profile


def render_enhanced_sidebar():
    with st.sidebar:
        st.markdown("---")

        if is_level_0_complete():
            voice_profile = get_voice_profile()
            completed = st.session_state.completed_exercises
            progress = get_level_progress(completed)

            st.markdown("<div class='section-label'>Progress</div>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)

            with col1:
                l0 = progress[0]
                st.metric("Level 0", f"{l0['percentage']}%", f"{l0['completed']}/{l0['total']}")

            with col2:
                l1 = progress[1]
                st.metric("Level 1", f"{l1['percentage']}%", f"{l1['completed']}/{l1['total']}")

            with col3:
                l2 = progress[2]
                st.metric("Level 2", f"{l2['percentage']}%", f"{l2['completed']}/{l2['total']}")

            st.markdown("---")

            st.markdown("<div class='section-label'>Exercises</div>", unsafe_allow_html=True)

            level_select = st.selectbox(
                "Level",
                options=[(f"Level {level} — {get_level_badge(level)}", level) for level in range(10)],
                format_func=lambda x: x[0],
                key="sidebar_level_select",
                label_visibility="collapsed",
            )

            selected_level = level_select[1]
            pages = get_pages_by_level(selected_level)

            for page_key in sorted(pages.keys(), key=lambda k: pages[k].get("order", 0)):
                page_info = pages[page_key]
                is_unlocked = is_page_unlocked(page_key, completed, voice_profile)
                title = page_info.get("title", page_key)

                # Strip leading emoji from title
                clean_title = title
                for prefix_char in ["🎤", "🎵", "👂", "💨", "🌬️", "✨", "🎼", "📈", "⚡", "📉", "🎶", "🎸", "🎯", "📊"]:
                    if clean_title.startswith(prefix_char):
                        clean_title = clean_title[len(prefix_char):].strip()
                        break

                is_completed = page_key in completed

                if is_unlocked:
                    status = "· " if is_completed else "  "
                    st.write(f"{status}{clean_title}")
                else:
                    st.markdown(f"<span style='opacity:0.45'>&nbsp;&nbsp;{clean_title} (locked)</span>", unsafe_allow_html=True)

            st.markdown("---")

            weak_areas = voice_profile.get("weak_areas", [])
            if weak_areas:
                st.markdown("<div class='section-label'>Focus areas</div>", unsafe_allow_html=True)
                for area in weak_areas:
                    st.write(f"· {area.replace('_', ' ').title()}")

        else:
            st.markdown("""
            **Welcome**

            Start with Level 0 to get a personalised coaching profile.
            """)

        st.markdown("---")

        with st.expander("About"):
            st.markdown("""
            **AI Vocal Coach** — ten levels:

            **Level 0** — Diagnostics (3 exercises)
            Assess your baseline and build a vocal profile.

            **Level 1** — Fundamentals (6 exercises)
            Breath support, onset, legato, tone.

            **Level 2** — Pitch & Scales (6 exercises)
            Scales, intervals, arpeggios, stability.

            **Levels 3–9** — Articulation, resonance, classical technique, and repertoire.
            """)


def render_page_header(page_key):
    from utils.pages_config import get_page_info
    page_info = get_page_info(page_key)

    if not page_info:
        return

    level = page_info.get("level")
    difficulty = page_info.get("difficulty")
    skills = page_info.get("skills", [])
    duration = page_info.get("duration_minutes", 0)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col1:
        st.markdown(f"Level {level}")

    with col2:
        if skills:
            st.markdown(f"Skills: {', '.join(skills[:2])}")

    with col3:
        if duration:
            st.markdown(f"{duration} min")

    if difficulty:
        st.caption(difficulty)
