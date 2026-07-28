import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        .stMetric { background-color: var(--secondary-background-color); padding: 15px; border-radius: 10px; }
        .badge { display: inline-block; padding: 0.25em 0.6em; font-size: 75%; font-weight: 700; line-height: 1; text-align: center; white-space: nowrap; vertical-align: baseline; border-radius: 0.5rem; color: #fff; }
        .badge-success { background-color: #28a745; }
        .badge-warning { background-color: #ffc107; color: #212529; }
        .badge-danger { background-color: #dc3545; }
        </style>
    """, unsafe_allow_html=True)

def display_header(title: str, subtitle: str):
    st.title(title)
    st.markdown(f"**{subtitle}**")
    st.divider()

def render_score_badge(score: int) -> str:
    if score >= 85: return f'<span class="badge badge-success">★★★★★ Excellent ({score})</span>'
    elif score >= 70: return f'<span class="badge badge-warning">★★★☆☆ Good ({score})</span>'
    else: return f'<span class="badge badge-danger">★☆☆☆☆ Try Again ({score})</span>'