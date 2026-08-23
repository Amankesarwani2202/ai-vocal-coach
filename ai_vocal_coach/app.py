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

# Level 3 — Articulation, Vowels & Consonants
level_3 = [
    st.Page(str(pages_dir / "15_Exercise_3.1_Pure_Italian_Vowels.py"), title="3.1 Pure Italian Vowels"),
    st.Page(str(pages_dir / "16_Exercise_3.2_Vowel_Consistency_Ascending.py"), title="3.2 Vowel Consistency"),
    st.Page(str(pages_dir / "17_Exercise_3.3_Vowel_Modification_High_Notes.py"), title="3.3 Vowel Modification"),
    st.Page(str(pages_dir / "18_Exercise_3.4_Consonant_Clarity.py"), title="3.4 Consonant Clarity"),
    st.Page(str(pages_dir / "19_Exercise_3.5_Tongue_Tension.py"), title="3.5 Releasing Tongue Tension"),
    st.Page(str(pages_dir / "20_Exercise_3.6_Diction_Challenge.py"), title="3.6 Diction Challenge"),
]

# Level 4 — Legato & Musical Line
level_4 = [
    st.Page(str(pages_dir / "21_Exercise_4.1_Connecting_Notes.py"), title="4.1 Connecting Notes"),
    st.Page(str(pages_dir / "22_Exercise_4.2_Legato_Scales.py"), title="4.2 Stepwise Melodies"),
    st.Page(str(pages_dir / "23_Exercise_4.3_Phrase_Shaping.py"), title="4.3 Breath Phrasing"),
    st.Page(str(pages_dir / "24_Exercise_4.4_Melodic_Etude.py"), title="4.4 Melodic Etude"),
]

# Level 5 — Rhythm, Pulse & Musical Timing
level_5 = [
    st.Page(str(pages_dir / "25_Exercise_5.1_Singing_Metronome.py"), title="5.1 Singing with a Metronome"),
    st.Page(str(pages_dir / "26_Exercise_5.2_Quarter_Note_Pulse.py"), title="5.2 Simple Rhythmic Patterns"),
    st.Page(str(pages_dir / "27_Exercise_5.3_Dotted_Rhythms.py"), title="5.3 Compound Time"),
    st.Page(str(pages_dir / "28_Exercise_5.4_Triplets.py"), title="5.4 Clapping & Singing"),
    st.Page(str(pages_dir / "29_Exercise_5.5_Syncopation.py"), title="5.5 Syncopation"),
]

nav = st.navigation(
    {
        "": [home],
        "Level 0 — Diagnostics": level_0,
        "Level 1 — Fundamentals": level_1,
        "Level 2 — Pitch & Scales": level_2,
        "Level 3 — Articulation": level_3,
        "Level 4 — Legato": level_4,
        "Level 5 — Rhythm": level_5,
    }
)

nav.run()
