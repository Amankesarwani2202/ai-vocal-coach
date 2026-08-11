from pathlib import Path
import sys

import streamlit as st

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.state import init_session_state

st.set_page_config(
    page_title="Vocal Coach",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_session_state()

# Build navigation with grouped sections
pages_dir = ROOT / "pages"

home = st.Page(str(pages_dir / "1_Dashboard.py"), title="Your Progress", default=True)

# Level 0 — Diagnostics
level_0 = [
    st.Page(str(pages_dir / "2a_Exercise_0.1_Warm_Up.py"), title="0.1 Vocal Warm-Up"),
    st.Page(str(pages_dir / "2b_Exercise_0.2_Range_Finder.py"), title="0.2 Range Finder"),
    st.Page(str(pages_dir / "2c_Exercise_0.3_Ear_Training.py"), title="0.3 Ear Training"),
]

# Level 1 — Fundamentals
level_1 = [
    st.Page(str(pages_dir / "3_Exercise_1.1_Diaphragmatic_Support.py"), title="1.1 Diaphragmatic Support"),
    st.Page(str(pages_dir / "4_Exercise_1.2_Silent_Breath.py"), title="1.2 Silent Breath"),
    st.Page(str(pages_dir / "5_Exercise_1.3_Smooth_Onset.py"), title="1.3 Smooth Onset"),
    st.Page(str(pages_dir / "6_Exercise_1.4_Legato.py"), title="1.4 Legato"),
    st.Page(str(pages_dir / "7_Exercise_1.5_Five_Note_Scale.py"), title="1.5 Five-Note Scale"),
    st.Page(str(pages_dir / "8_Exercise_1.6_Staccato_vs_Legato.py"), title="1.6 Staccato vs Legato"),
]

# Level 2 — Pitch & Scales
level_2 = [
    st.Page(str(pages_dir / "9_Exercise_2.1_Major_Scale_Ascending.py"), title="2.1 Major Scale Ascending"),
    st.Page(str(pages_dir / "10_Exercise_2.2_Major_Scale_Descending.py"), title="2.2 Major Scale Descending"),
    st.Page(str(pages_dir / "11_Exercise_2.3_Minor_Scales.py"), title="2.3 Minor Scales"),
    st.Page(str(pages_dir / "12_Exercise_2.4_Intervals.py"), title="2.4 Intervals"),
    st.Page(str(pages_dir / "13_Exercise_2.5_Arpeggios.py"), title="2.5 Arpeggios"),
    st.Page(str(pages_dir / "14_Exercise_2.6_Pitch_Stability.py"), title="2.6 Pitch Stability"),
]

nav = st.navigation(
    {
        "": [home],
        "Level 0 — Diagnostics": level_0,
        "Level 1 — Fundamentals": level_1,
        "Level 2 — Pitch & Scales": level_2,
    }
)

nav.run()
