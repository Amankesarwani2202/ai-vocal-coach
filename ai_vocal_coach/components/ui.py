import streamlit as st
import streamlit.components.v1 as components
import numpy as np
import io
import wave

from utils.state import get_user_profile, update_user_name, get_current_theme, toggle_theme


def inject_custom_css():
    theme = get_current_theme()

    if theme == "dark":
        bg = "#111210"
        bg_surface = "#1A1A18"
        text = "#F0EDE8"
        text_muted = "#8A8680"
        border = "#2E2C28"
        accent = "#C97B2A"
        accent_light = "rgba(201, 123, 42, 0.12)"
        success = "#4A9B6F"
        success_light = "rgba(74, 155, 111, 0.12)"
        warning_light = "rgba(201, 123, 42, 0.1)"
        btn_text = "#F0EDE8"
        input_bg = "#1A1A18"
    else:
        bg = "#F8F5F0"
        bg_surface = "#FFFFFF"
        text = "#1A1A1A"
        text_muted = "#6B6560"
        border = "#E2DDD6"
        accent = "#B45309"
        accent_light = "rgba(180, 83, 9, 0.08)"
        success = "#166534"
        success_light = "rgba(22, 101, 52, 0.08)"
        warning_light = "rgba(180, 83, 9, 0.06)"
        btn_text = "#FFFFFF"
        input_bg = "#FFFFFF"

    css = f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');

        :root {{
            --bg: {bg};
            --bg-surface: {bg_surface};
            --text: {text};
            --text-muted: {text_muted};
            --border: {border};
            --accent: {accent};
            --accent-light: {accent_light};
            --success: {success};
            --success-light: {success_light};
        }}

        html, body, .stApp {{
            background-color: {bg} !important;
            color: {text};
            font-family: 'DM Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        }}

        [data-testid="stVerticalBlock"],
        [data-testid="stMain"],
        section.main {{
            background-color: {bg} !important;
        }}

        /* Remove Streamlit default top padding */
        .block-container {{
            padding-top: 1.5rem !important;
            max-width: 900px;
        }}

        /* Typography hierarchy */
        h1 {{
            font-size: 2rem;
            font-weight: 700;
            color: {text};
            letter-spacing: -0.02em;
            margin-bottom: 0.25rem;
            font-family: 'Fraunces', Georgia, serif;
            letter-spacing: 0;
        }}

        h2 {{
            font-size: 1.5rem;
            font-weight: 600;
            color: {text};
            letter-spacing: -0.01em;
        }}

        h3 {{
            font-size: 1.15rem;
            font-weight: 600;
            color: {text};
        }}

        h4, h5, h6 {{
            color: {text};
        }}

        p, li {{
            color: {text};
            line-height: 1.65;
        }}

        /* Eyebrow label above headings */
        .eyebrow {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {accent};
            margin-bottom: 0.4rem;
        }}

        /* Dividers */
        hr, .stDivider {{
            border: none;
            border-top: 1px solid {border};
            margin: 1.75rem 0;
        }}

        /* Metrics — plain, no gradient boxes */
        [data-testid="stMetric"] {{
            background: {bg_surface};
            border: 1px solid {border};
            border-radius: 6px;
            padding: 1rem 1.25rem;
        }}

        [data-testid="stMetricLabel"] {{
            font-size: 0.75rem !important;
            font-weight: 500 !important;
            color: {text_muted} !important;
            text-transform: uppercase;
            letter-spacing: 0.06em;
        }}

        [data-testid="stMetricValue"] {{
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: {text} !important;
        }}

        [data-testid="stMetricDelta"] {{
            color: {success} !important;
        }}

        /* Exercise hero section — the main focus */
        .exercise-hero {{
            margin-bottom: 2rem;
        }}

        .exercise-hero .exercise-number {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {accent};
            margin-bottom: 0.4rem;
        }}

        .exercise-hero h1 {{
            font-size: 2.25rem;
            font-weight: 700;
            line-height: 1.15;
            color: {text};
            margin-bottom: 0.5rem;
        }}

        .exercise-hero .subtitle {{
            font-size: 1.05rem;
            color: {text_muted};
            margin-bottom: 1.25rem;
        }}

        .exercise-meta {{
            display: flex;
            gap: 1.5rem;
            flex-wrap: wrap;
            padding: 0.85rem 0;
            border-top: 1px solid {border};
            border-bottom: 1px solid {border};
            margin: 1rem 0;
        }}

        .exercise-meta-item {{
            font-size: 0.8rem;
            color: {text_muted};
        }}

        .exercise-meta-item strong {{
            color: {text};
            font-weight: 600;
        }}

        /* Stage indicator — minimal, horizontal */
        .stage-bar {{
            display: flex;
            align-items: center;
            gap: 0;
            margin-bottom: 2rem;
        }}

        .stage-step {{
            font-size: 0.75rem;
            font-weight: 500;
            color: {text_muted};
            padding: 0.4rem 0;
        }}

        .stage-step.active {{
            color: {accent};
            font-weight: 600;
            border-bottom: 2px solid {accent};
        }}

        .stage-step.done {{
            color: {success};
        }}

        .stage-sep {{
            width: 32px;
            height: 1px;
            background: {border};
            margin: 0 0.5rem;
        }}

        /* Audio exemplar block */
        .exemplar-block {{
            background: {bg_surface};
            border: 1px solid {border};
            border-left: 3px solid {accent};
            border-radius: 4px;
            padding: 1rem 1.25rem;
            margin: 1.25rem 0;
        }}

        .exemplar-block .exemplar-label {{
            font-size: 0.72rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {text_muted};
            margin-bottom: 0.5rem;
        }}

        /* Instruction steps */
        .instruction-step {{
            display: flex;
            gap: 1rem;
            padding: 0.65rem 0;
            border-bottom: 1px solid {border};
            align-items: flex-start;
        }}

        .instruction-step:last-child {{
            border-bottom: none;
        }}

        .step-number {{
            font-size: 0.75rem;
            font-weight: 700;
            color: {accent};
            min-width: 20px;
            padding-top: 0.1rem;
        }}

        .step-text {{
            font-size: 0.92rem;
            color: {text};
            line-height: 1.5;
        }}

        /* Feedback timeline items */
        .feedback-item {{
            display: flex;
            gap: 1rem;
            padding: 0.7rem 0;
            border-bottom: 1px solid {border};
            align-items: flex-start;
        }}

        .feedback-item:last-child {{
            border-bottom: none;
        }}

        .feedback-timestamp {{
            font-size: 0.72rem;
            font-weight: 600;
            color: {accent};
            font-family: 'SF Mono', 'Fira Code', monospace;
            min-width: 44px;
            padding-top: 0.15rem;
            cursor: pointer;
        }}

        .feedback-text {{
            font-size: 0.9rem;
            color: {text};
            line-height: 1.5;
        }}

        /* Coaching summary sections */
        .coaching-section {{
            padding: 1rem 0;
            border-bottom: 1px solid {border};
        }}

        .coaching-section:last-child {{
            border-bottom: none;
        }}

        .coaching-section-label {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {text_muted};
            margin-bottom: 0.4rem;
        }}

        .coaching-text {{
            font-size: 0.92rem;
            color: {text};
            line-height: 1.6;
        }}

        /* Notice / info box — flat, no box */
        .notice-box {{
            background: {accent_light};
            border-left: 3px solid {accent};
            padding: 0.85rem 1rem;
            border-radius: 3px;
            font-size: 0.9rem;
            color: {text};
            margin: 1rem 0;
        }}

        .notice-success {{
            background: {success_light};
            border-left: 3px solid {success};
        }}

        /* Profile header — minimal */
        .profile-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.5rem 0 1rem 0;
            border-bottom: 1px solid {border};
            margin-bottom: 1.5rem;
        }}

        .profile-header .user-name {{
            font-size: 0.82rem;
            color: {text_muted};
        }}

        .profile-header .session-info {{
            font-size: 0.72rem;
            color: {text_muted};
        }}

        /* Progress bars — clean */
        .stProgress > div > div {{
            background-color: {accent} !important;
            border-radius: 2px;
        }}

        .stProgress > div {{
            background-color: {border} !important;
            border-radius: 2px;
            height: 4px !important;
        }}

        /* Buttons — clean, solid */
        .stButton > button {{
            background: {accent} !important;
            color: {btn_text} !important;
            border: none !important;
            border-radius: 5px !important;
            padding: 0.6rem 1.5rem !important;
            font-weight: 600 !important;
            font-size: 0.88rem !important;
            letter-spacing: 0.01em;
            transition: background 0.2s ease !important;
            box-shadow: none !important;
        }}

        .stButton > button:hover {{
            background: {accent} !important;
            opacity: 0.88;
            transform: none !important;
            box-shadow: none !important;
        }}

        .stButton > button:active {{
            opacity: 0.75 !important;
        }}

        /* Secondary button style — use data attribute workaround via disabled styling */
        button[kind="secondary"] {{
            background: transparent !important;
            color: {accent} !important;
            border: 1px solid {accent} !important;
        }}

        /* Dataframe */
        .stDataFrame {{
            border: 1px solid {border};
            border-radius: 4px;
        }}

        /* Alerts */
        [data-testid="stAlert"] {{
            border-radius: 4px !important;
            border: none !important;
            border-left: 3px solid {accent} !important;
            background: {accent_light} !important;
        }}

        /* Sidebar — see responsive rules near bottom of this block */
        [data-testid="stSidebar"] * {{
            color: {text} !important;
        }}

        [data-testid="stSidebarCollapseButton"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebarCollapseButton"] svg {{
            width: 1rem !important;
            height: 1rem !important;
        }}

        /* Input fields */
        .stTextInput > div > div > input {{
            background: {input_bg} !important;
            border: 1px solid {border} !important;
            border-radius: 5px !important;
            color: {text} !important;
        }}

        /* Expander */
        [data-testid="stExpander"] {{
            border: 1px solid {border} !important;
            border-radius: 5px !important;
            background: {bg_surface} !important;
        }}

        /* Select box */
        .stSelectbox > div > div {{
            background: {input_bg} !important;
            border-color: {border} !important;
        }}

        /* Captions */
        .stCaption, [data-testid="stCaptionContainer"] {{
            color: {text_muted} !important;
            font-size: 0.78rem !important;
        }}

        /* Theme toggle */
        .theme-toggle {{
            position: fixed;
            top: 60px;
            right: 14px;
            z-index: 999;
        }}

        /* Audio player */
        audio {{
            width: 100%;
            border-radius: 4px;
        }}

        /* Breathing circle container */
        .breathing-container {{
            text-align: center;
            padding: 1.5rem 0;
        }}

        /* Dashboard section header — flat */
        .section-label {{
            font-size: 0.7rem;
            font-weight: 600;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: {text_muted};
            margin-bottom: 1rem;
        }}

        /* Score badge — text-only, no boxes */
        .score-badge {{
            font-size: 0.85rem;
            font-weight: 600;
        }}

        .score-good {{ color: {success}; }}
        .score-ok {{ color: {accent}; }}
        .score-low {{ color: #9B2335; }}

        /* Noise warning */
        .noise-warning {{
            background: rgba(155, 35, 53, 0.08);
            border-left: 3px solid #9B2335;
            padding: 0.85rem 1rem;
            border-radius: 3px;
            margin: 1rem 0;
        }}

        /* Recording indicator */
        .recording-dot {{
            display: inline-block;
            width: 8px;
            height: 8px;
            background: #DC2626;
            border-radius: 50%;
            margin-right: 6px;
            animation: pulse 1.2s ease-in-out infinite;
        }}

        @keyframes pulse {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.3; }}
        }}

        /* ── Ear Training: round progress ── */
        .round-progress-header {{
            display: flex;
            align-items: center;
            gap: 0.75rem;
            margin-bottom: 0.75rem;
        }}
        .round-label {{
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            color: {text_muted};
        }}
        .round-note-chip {{
            font-size: 0.78rem;
            font-weight: 700;
            color: {accent};
            background: {accent_light};
            border: 1px solid {accent};
            border-radius: 999px;
            padding: 0.15rem 0.6rem;
            letter-spacing: 0.04em;
        }}
        .round-dots {{
            display: flex;
            gap: 0.45rem;
            margin-bottom: 1.25rem;
        }}
        .round-dot {{
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: {border};
            transition: background 0.2s ease;
        }}
        .round-dot.active {{
            background: {accent};
        }}
        .round-dot.done {{
            background: {success};
        }}

        /* ── Ear Training: reference tone card ── */
        .round-card {{
            background: {bg_surface};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 1.25rem 1.5rem;
            margin: 0.75rem 0 1.25rem 0;
        }}
        .round-card-label {{
            font-size: 0.68rem;
            font-weight: 600;
            letter-spacing: 0.1em;
            text-transform: uppercase;
            color: {text_muted};
            margin-bottom: 0.5rem;
        }}
        .round-card-note {{
            font-size: 2.5rem;
            font-weight: 700;
            color: {accent};
            letter-spacing: -0.02em;
            line-height: 1;
        }}
        .round-card-hz {{
            font-size: 0.85rem;
            color: {text_muted};
            margin-top: 0.2rem;
        }}

        /* ── Ear Training: pitch result card ── */
        .pitch-result-card {{
            text-align: center;
        }}
        .round-result-row {{
            margin-bottom: 0.2rem;
        }}
        .round-result-label {{
            font-size: 0.95rem;
            font-weight: 600;
            margin-bottom: 0.4rem;
        }}
        .pitch-deviation {{
            font-size: 1.05rem;
            font-weight: 600;
            color: {accent};
            margin: 0.3rem 0;
            font-family: 'SF Mono', 'Fira Code', monospace;
        }}
        .pitch-sung-hz {{
            font-size: 0.78rem;
            color: {text_muted};
            margin-top: 0.25rem;
        }}

        /* ── Ear Training: summary table ── */
        .et-summary-row {{
            display: flex;
            align-items: center;
            gap: 1rem;
            padding: 0.65rem 0;
            border-bottom: 1px solid {border};
            flex-wrap: wrap;
        }}
        .et-summary-row:last-child {{
            border-bottom: none;
        }}
        .et-round-note {{
            font-size: 1rem;
            font-weight: 700;
            color: {accent};
            min-width: 2.5rem;
        }}
        .et-round-score {{
            font-size: 0.88rem;
            font-weight: 600;
            min-width: 4rem;
        }}
        .et-round-quality {{
            font-size: 0.88rem;
            color: {text};
            flex: 1;
        }}
        .et-round-cents {{
            font-size: 0.82rem;
            color: {text_muted};
            font-family: 'SF Mono', 'Fira Code', monospace;
        }}

        /* ── Stage bar: arrow prefix on active step ── */
        .stage-step.active::before {{
            content: '▸ ';
            color: {accent};
            font-size: 0.7rem;
        }}

        /* ── Instruction step: subtle hover ── */
        .instruction-step:hover {{
            background: {accent_light};
            border-radius: 4px;
            margin: 0 -0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}

        /* ── Feedback item: subtle hover ── */
        .feedback-item:hover {{
            background: {warning_light};
            border-radius: 4px;
            margin: 0 -0.5rem;
            padding-left: 0.5rem;
            padding-right: 0.5rem;
        }}

        /* ── Card utility class ── */
        .card {{
            background: {bg_surface};
            border: 1px solid {border};
            border-radius: 8px;
            padding: 1rem 1.25rem;
        }}

        /* ── Button: smoother hover via opacity transition ── */
        .stButton > button {{
            transition: background 0.2s ease, opacity 0.15s ease !important;
        }}

        /* Hide footer and Streamlit menu */
        #MainMenu, footer {{
            display: none !important;
        }}

        /* Streamlit header — blend into page bg, keep in DOM so sidebar works */
        [data-testid="stHeader"] {{
            background: {bg} !important;
            border: none !important;
            box-shadow: none !important;
        }}

        [data-testid="stToolbar"] {{
            display: none !important;
        }}

        /* ── Sidebar base styling (all screen sizes) ── */
        [data-testid="stSidebar"] {{
            background: {bg_surface} !important;
            border-right: 1px solid {border} !important;
        }}

        [data-testid="stSidebarContent"] {{
            background: {bg_surface} !important;
            padding-top: 1rem !important;
        }}

        [data-testid="stSidebarNav"]::before {{
            content: none !important;
        }}

        [data-testid="stSidebarNavLink"] {{
            color: {text} !important;
            border-radius: 4px !important;
            padding: 0.45rem 0.75rem !important;
            font-size: 0.88rem !important;
            transition: background 0.15s ease !important;
        }}

        [data-testid="stSidebarNavLink"]:hover {{
            background: {accent_light} !important;
        }}

        [data-testid="stSidebarNavLink"][aria-current="page"] {{
            background: {accent_light} !important;
            color: {accent} !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebarNavLink"][aria-current="page"] * {{
            color: {accent} !important;
        }}

        [data-testid="stSidebarNavSeparator"] {{
            border-top: 1px solid {border} !important;
            margin: 0.4rem 0.75rem !important;
        }}

        /* Collapse button (<<) inside the sidebar — subtle */
        [data-testid="stSidebarCollapseButton"] button {{
            background: transparent !important;
            border: none !important;
            color: {text_muted} !important;
            border-radius: 4px !important;
        }}

        [data-testid="stSidebarCollapseButton"] button:hover {{
            background: {accent_light} !important;
            color: {accent} !important;
        }}

        /* Re-open button (>) shown when sidebar is collapsed — must stay visible */
        [data-testid="stSidebarCollapsedControl"] {{
            display: flex !important;
            visibility: visible !important;
            opacity: 1 !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button {{
            background: {bg_surface} !important;
            border: 1px solid {border} !important;
            color: {accent} !important;
            border-radius: 0 4px 4px 0 !important;
            box-shadow: 2px 0 6px rgba(0,0,0,0.08) !important;
        }}

        [data-testid="stSidebarCollapsedControl"] button:hover {{
            background: {accent_light} !important;
        }}

        /* ── Desktop (≥768px): sidebar always pinned open ── */
        @media (min-width: 768px) {{
            [data-testid="stSidebar"],
            [data-testid="stSidebarContent"] {{
                display: flex !important;
                visibility: visible !important;
                transform: translateX(0) !important;
                min-width: 15rem !important;
                width: 15rem !important;
            }}
            /* Hide << on desktop — it can't function when sidebar is force-pinned */
            [data-testid="stSidebarCollapseButton"] {{
                display: none !important;
            }}
            .block-container {{
                padding-top: 4rem !important;
                padding-left: 2rem !important;
                padding-right: 2rem !important;
                max-width: 900px;
            }}
        }}

        /* ── Mobile (<768px): sidebar as overlay drawer ── */
        @media (max-width: 767px) {{
            /* Sidebar slides in as a fixed overlay; Streamlit drives the transform */
            [data-testid="stSidebar"] {{
                position: fixed !important;
                top: 0 !important;
                left: 0 !important;
                height: 100dvh !important;
                z-index: 1001 !important;
                width: 80vw !important;
                min-width: 0 !important;
                max-width: 300px !important;
                box-shadow: 4px 0 24px rgba(0,0,0,0.22) !important;
            }}
            /* Keep the native << close button visible inside the sidebar */
            [data-testid="stSidebarCollapseButton"] {{
                display: flex !important;
            }}
            /* Style the native > reopen button as a prominent fixed menu button */
            [data-testid="stSidebarCollapsedControl"] {{
                display: flex !important;
                visibility: visible !important;
                opacity: 1 !important;
                position: fixed !important;
                top: 10px !important;
                left: 10px !important;
                z-index: 9999 !important;
            }}
            [data-testid="stSidebarCollapsedControl"] button {{
                background: {bg_surface} !important;
                border: 1.5px solid {border} !important;
                border-radius: 8px !important;
                padding: 8px 14px !important;
                font-size: 1.25rem !important;
                line-height: 1 !important;
                box-shadow: 0 2px 10px rgba(0,0,0,0.15) !important;
                color: {accent} !important;
                width: auto !important;
            }}

            /* Content always uses full viewport width on mobile */
            .block-container {{
                padding-top: 3.75rem !important;
                padding-left: 0.85rem !important;
                padding-right: 0.85rem !important;
                max-width: 100% !important;
                margin-left: 0 !important;
            }}

            /* Show hamburger icon in title only on mobile */
            .vc-menu-icon {{
                display: inline !important;
            }}

            /* Larger touch targets for nav links on mobile */
            [data-testid="stSidebarNavLink"] {{
                padding: 0.65rem 0.85rem !important;
                font-size: 0.95rem !important;
            }}

            /* Shrink hero heading on small screens */
            .exercise-hero h1 {{
                font-size: 1.6rem !important;
            }}

            h1 {{
                font-size: 1.65rem !important;
            }}

            /* Stage bar: tighter on mobile */
            .stage-bar {{
                margin-bottom: 1.25rem !important;
            }}

            .stage-step {{
                font-size: 0.7rem !important;
            }}

            /* Metrics: let them stack naturally */
            [data-testid="stMetric"] {{
                padding: 0.7rem 0.9rem !important;
            }}

            [data-testid="stMetricValue"] {{
                font-size: 1.3rem !important;
            }}

            /* Buttons: full width on mobile */
            .stButton > button {{
                width: 100% !important;
                padding: 0.7rem 1rem !important;
            }}

            /* Reduce outer margins */
            .exercise-hero {{
                margin-bottom: 1.25rem !important;
            }}

            /* Audio full width */
            audio {{
                width: 100% !important;
            }}
        }}

        /* ── Vowel cards (3.1) ─────────────────── */
        .vowel-card-grid {{
            display: grid;
            grid-template-columns: repeat(5, 1fr);
            gap: 0.5rem;
            margin: 1rem 0;
        }}
        .vowel-card {{
            background: {bg_surface};
            border: 2px solid {border};
            border-radius: 12px;
            padding: 1rem 0.5rem;
            text-align: center;
            transition: border-color 0.2s, transform 0.1s;
        }}
        .vowel-card.active {{
            border-color: {accent};
            transform: scale(1.04);
        }}
        .vowel-card.done {{
            border-color: {success};
            opacity: 0.7;
        }}
        .vowel-card-letter {{
            font-size: 2rem;
            font-weight: 700;
            color: {accent};
            line-height: 1;
        }}
        .vowel-card-ipa {{
            font-size: 0.75rem;
            color: {text_muted};
            margin-top: 0.25rem;
        }}

        /* ── Tension meter (3.5) ──────────────── */
        .tension-meter-wrap {{
            margin: 1rem 0;
        }}
        .tension-meter-track {{
            height: 14px;
            border-radius: 7px;
            background: linear-gradient(90deg, {success} 0%, {accent} 60%, #C0392B 100%);
            position: relative;
        }}
        .tension-meter-needle {{
            position: absolute;
            top: -4px;
            width: 4px;
            height: 22px;
            background: {text};
            border-radius: 2px;
            transform: translateX(-50%);
        }}
        .tension-meter-labels {{
            display: flex;
            justify-content: space-between;
            font-size: 0.7rem;
            color: {text_muted};
            margin-top: 4px;
        }}

        /* ── Legato ribbon (4.x) ──────────────── */
        .legato-ribbon {{
            height: 8px;
            border-radius: 4px;
            margin: 0.75rem 0;
            background: linear-gradient(90deg,
                {accent_light} 0%,
                {accent} 40%,
                {accent} 60%,
                {accent_light} 100%);
        }}
        .legato-gap-marker {{
            display: inline-block;
            width: 3px;
            height: 16px;
            background: #C0392B;
            border-radius: 2px;
            margin: 0 2px;
            vertical-align: middle;
        }}

        /* ── Metronome beat display (5.x) ─────── */
        .beat-grid {{
            display: flex;
            gap: 0.4rem;
            margin: 0.75rem 0;
            flex-wrap: wrap;
        }}
        .beat-cell {{
            width: 36px;
            height: 36px;
            border-radius: 8px;
            background: {bg_surface};
            border: 2px solid {border};
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.7rem;
            color: {text_muted};
            transition: background 0.15s;
        }}
        .beat-cell.downbeat {{
            border-color: {accent};
            color: {accent};
            font-weight: 600;
        }}
        .beat-cell.on-time {{
            background: {success_light};
            border-color: {success};
            color: {success};
        }}
        .beat-cell.late {{
            background: {warning_light};
            border-color: {accent};
            color: {accent};
        }}
        .beat-cell.missed {{
            background: rgba(192, 57, 43, 0.1);
            border-color: #C0392B;
            color: #C0392B;
        }}

        /* ── Diction 2-phase (3.6) ────────────── */
        .diction-phrase-card {{
            background: {bg_surface};
            border: 2px solid {accent};
            border-radius: 12px;
            padding: 1.25rem 1.5rem;
            margin: 1rem 0;
            font-size: 1.3rem;
            font-style: italic;
            color: {text};
            text-align: center;
            letter-spacing: 0.01em;
        }}
        .phase-step-bar {{
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }}
        .phase-step {{
            flex: 1;
            height: 4px;
            border-radius: 2px;
            background: {border};
        }}
        .phase-step.active {{
            background: {accent};
        }}
        .phase-step.done {{
            background: {success};
        }}
        </style>
    """
    st.markdown(css, unsafe_allow_html=True)


def render_top_nav(current_page="home"):
    """Render centred brand bar at top of every page."""
    profile = get_user_profile()
    name = profile["name"] if profile["name"] != "Guest" else ""

    right_slot = (
        f'<span style="font-size:1rem;color:var(--text-primary,#1C1917);font-weight:500;white-space:nowrap">{name}</span>'
        if name else
        '<span></span>'
    )

    st.markdown(
        f'''<div style="
                display:grid;
                grid-template-columns:1fr auto 1fr;
                align-items:center;
                padding:0.6rem 0 0.75rem 0;
                margin-bottom:1.25rem;
                border-bottom:1px solid var(--border,#E2DDD6);
            ">
            <span></span>
            <a id="vc-title" href="/" style="
                text-decoration:none;
                color:var(--accent,#B45309) !important;
                font-weight:700;
                font-size:1.25rem;
                letter-spacing:-0.01em;
                text-align:center;
                cursor:pointer;
            "><span style="display:none" class="vc-menu-icon">☰ </span>🎙 Vocal Coach</a>
            <span style="text-align:right">{right_slot}</span>
        </div>''',
        unsafe_allow_html=True,
    )

    # Tapping the title toggles the sidebar; a dark backdrop lets user close by tapping outside.
    components.html(
        """
        <script>
        (function() {
            var p = window.parent.document;
            var w = window.parent;

            // Inject backdrop CSS once
            if (!p.getElementById('vc-backdrop-style')) {
                var s = p.createElement('style');
                s.id = 'vc-backdrop-style';
                s.textContent =
                    '#vc-backdrop{display:none;position:fixed;top:0;left:0;right:0;bottom:0;' +
                    'z-index:1000;background:rgba(0,0,0,0.45);pointer-events:none;}' +
                    '#vc-backdrop.vc-backdrop-active{pointer-events:auto;}' +
                    '@media (min-width:768px){#vc-backdrop{display:none !important;}}';
                p.head.appendChild(s);
            }

            // Create backdrop in parent body once
            var back = p.getElementById('vc-backdrop');
            if (!back) {
                back = p.createElement('div');
                back.id = 'vc-backdrop';
                p.body.appendChild(back);
            }

            function getSidebar() {
                return p.querySelector('[data-testid="stSidebar"]');
            }
            function isOpen() {
                var sb = getSidebar();
                if (!sb) return false;
                var t = w.getComputedStyle(sb).transform;
                return !t || t === 'none' || t === 'matrix(1, 0, 0, 1, 0, 0)';
            }
            function openSidebar() {
                var o = p.querySelector('[data-testid="stSidebarCollapsedControl"] button');
                if (o) { o.click(); return; }
                var sb = getSidebar();
                if (sb) { sb.style.transform = 'translateX(0)'; sb.style.visibility = 'visible'; }
            }
            function closeSidebar() {
                var c = p.querySelector('[data-testid="stSidebarCollapseButton"] button');
                if (c) { c.click(); return; }
                var sb = getSidebar();
                if (sb) sb.style.transform = 'translateX(-100%)';
            }
            function isMobile() {
                return w.innerWidth < 768;
            }
            function syncBackdrop() {
                setTimeout(function() {
                    var show = isMobile() && isOpen();
                    back.style.display = show ? 'block' : 'none';
                    back.classList.toggle('vc-backdrop-active', show);
                }, 120);
            }

            // Backdrop tap → close
            back.addEventListener('click', function() {
                closeSidebar();
                syncBackdrop();
            });

            // Title tap → toggle
            function wireTitle() {
                var title = p.getElementById('vc-title');
                if (!title) { setTimeout(wireTitle, 150); return; }
                title.addEventListener('click', function(e) {
                    e.preventDefault();
                    if (isOpen()) { closeSidebar(); } else { openSidebar(); }
                    syncBackdrop();
                });
            }
            wireTitle();

            // Keep backdrop in sync when Streamlit itself changes sidebar state
            var obs = new MutationObserver(syncBackdrop);
            function watchSidebar() {
                var sb = getSidebar();
                if (sb) {
                    obs.observe(sb, { attributes: true, attributeFilter: ['style','class'] });
                    syncBackdrop();
                } else { setTimeout(watchSidebar, 200); }
            }
            watchSidebar();
        })();
        </script>
        """,
        height=1,
    )


def render_theme_toggle():
    pass


def render_profile_card(show_editor: bool = False):
    pass


def display_header(title: str, subtitle: str, show_profile_editor: bool = False):
    render_top_nav("home")
    st.title(title)
    if subtitle:
        st.markdown(f"<p style='color:var(--text-muted,#6B6560);margin-top:-0.5rem'>{subtitle}</p>", unsafe_allow_html=True)
    st.divider()


def render_score_badge(score: int) -> str:
    if score >= 85:
        return f'<span class="score-badge score-good">Excellent &mdash; {score}/100</span>'
    if score >= 70:
        return f'<span class="score-badge score-ok">Good &mdash; {score}/100</span>'
    return f'<span class="score-badge score-low">Keep Practicing &mdash; {score}/100</span>'


def generate_tone(frequency: float, duration: float = 2.0, sr: int = 16000) -> bytes:
    t = np.linspace(0, duration, int(sr * duration), False)
    audio = np.sin(2 * np.pi * frequency * t) * 0.3

    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sr)
        audio_int16 = (audio * 32767).astype(np.int16)
        wav_file.writeframes(audio_int16.tobytes())
    wav_buffer.seek(0)
    return wav_buffer.getvalue()
