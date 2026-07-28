import streamlit as st

from utils.state import get_user_profile, update_user_name


def inject_custom_css():
    st.markdown(
        """
        <style>
        .stMetric { background-color: var(--secondary-background-color); padding: 15px; border-radius: 12px; }
        .badge { display: inline-block; padding: 0.25em 0.6em; font-size: 75%; font-weight: 700; line-height: 1; text-align: center; white-space: nowrap; vertical-align: baseline; border-radius: 0.5rem; color: #fff; }
        .badge-success { background-color: #28a745; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-danger { background-color: #dc3545; }
        .hero-card {
            background: linear-gradient(135deg, #2563eb, #7c3aed);
            border-radius: 16px;
            padding: 18px 20px;
            color: white;
            margin-bottom: 16px;
            box-shadow: 0 8px 24px rgba(37, 99, 235, 0.25);
        }
        .hero-card .eyebrow {
            font-size: 0.8rem;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            opacity: 0.9;
            margin-bottom: 6px;
        }
        .pill {
            display: inline-block;
            background: rgba(255,255,255,0.16);
            padding: 6px 10px;
            border-radius: 999px;
            font-size: 0.85rem;
            margin-top: 8px;
        }
        .block-container {
            padding-top: 1rem;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_profile_card(show_editor: bool = False):
    profile = get_user_profile()
    st.markdown(
        f"""
        <div class="hero-card">
            <div class="eyebrow">Personal coaching profile</div>
            <h3 style="margin: 0;">Welcome back, {profile['name']} 👋</h3>
            <div style="margin-top: 6px;">Session #{profile['session_id']} • Started {profile['session_started_at']}</div>
            <div class="pill">🎯 Focus: breath support, tone, and confidence</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if show_editor:
        with st.expander("Edit profile", expanded=False):
            new_name = st.text_input(
                "Your name",
                value=st.session_state.get("user_name", ""),
                key="profile_name_input",
            )
            if st.button("Save profile", use_container_width=True):
                update_user_name(new_name)
                st.session_state["profile_name_updated"] = True
                st.rerun()


def display_header(title: str, subtitle: str, show_profile_editor: bool = False):
    render_profile_card(show_profile_editor)
    st.title(title)
    st.markdown(f"**{subtitle}**")
    st.divider()


def render_score_badge(score: int) -> str:
    if score >= 85:
        return f'<span class="badge badge-success">★★★★★ Excellent ({score})</span>'
    if score >= 70:
        return f'<span class="badge badge-warning">★★★☆☆ Good ({score})</span>'
    return f'<span class="badge badge-danger">★☆☆☆☆ Try Again ({score})</span>'