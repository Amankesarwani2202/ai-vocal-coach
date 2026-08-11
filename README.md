# AI Vocal Coach 🎤

> **Status:  PREMIUM FEATURES ARCHITECTURE READY**

A premium AI-powered singing coach that feels like **Duolingo meets Yousician meets Apple Health**. Interactive, beginner-friendly, and incredibly encouraging. Built on Streamlit with YIN-based pitch detection and comprehensive vocal training exercises across three levels.

**Quick Start:** `streamlit run ai_vocal_coach/app.py`

**Premium Feel Achieved:**
-  Duolingo-style clear progression and sensible gamification
-  Yousician-style interactive visual exercises  
-  Apple Health-style clear & useful analytics
-  Beginner-friendly (no technical jargon, always encouraging)

## ✨ Features

### 🎙️ Voice Analysis
- **YIN-Based Pitch Detection:** Autocorrelation pitch tracking with accurate Hz-to-note conversion
- **Real-Time Acoustic Metrics:** Pitch accuracy, stability, breath consistency, tone quality
- **Voice Type Classification:** Auto-detects soprano/mezzo/alto/tenor/baritone/bass from vocal range
- **Advanced Metrics:** Pitch sagging, register breaks, interval accuracy, time-domain analysis

### 📚 Three-Level Training
- **Level 0: Diagnostics** (3 exercises) — Vocal profile assessment and placement routing
- **Level 1: Fundamentals** (6 exercises) — Breath support, tone control, legato/staccato
- **Level 2: Pitch & Scales** (6 exercises) — Major/minor scales, intervals, arpeggios, pitch stability

### 🎨 Enhanced UI/UX

- **Dual-Theme Support:** Toggle between light and dark themes instantly (☀️/🌙 button in sidebar)
- **Modern Gradient Design:** Sleek purple-to-green color scheme with smooth animations
- **Interactive Gauges:** Real-time pitch stability visualizations
- **Radar Charts:** Multi-dimensional performance scoring
- **Responsive Layouts:** Mobile-friendly exercise pages with clear instructions
- **Rich Feedback:** Contextual hints, tips, and personalized coaching
- **Premium Dashboard:** Beautiful welcome banners, progress cards, and activity tracking

### 🏆 Gamification & Enhanced Dashboard
- **XP System:** Earn points for each completed exercise with milestone tracking
- **Progress Tracking:** Visual completion indicators (✅ vs ⭕) for all exercises
- **Progress Bars:** Visual representation of completion % for each level
- **Best Score Recording:** Track improvement over time with color-coded badges (🟢 Great / 🟡 Good / 🔴 Try Again)
- **Voice Profile Card:** Persistent vocal metrics (range, voice type, focus areas, placement level)
- **Enhanced Sidebar:** Real-time progress by level, quick navigation, lock icons, difficulty indicators
- **Level Progression Display:** See completion % for Level 0, 1, and 2 with exercise breakdown
- **Recommended Focus Areas:** Personalized coaching based on weak areas from Level 0
- **Next Exercise Guidance:** Smart recommendations for what to practice next
- **Recent Activity Tracker:** Session history with scores and statistics
- **Session Statistics:** Total sessions, best session score, average session score

## 📖 Standardized Page Naming Convention



All pages follow a **unified naming pattern** for consistency and maintainability:

**Format:** `{ORDER}_{Exercise}_{LEVEL}.{NUMBER}_{TITLE}.py`

**Examples:**

- Dashboard: `1_Dashboard.py`
- Level 0: `2a_Exercise_0.1_Warm_Up.py`, `2b_Exercise_0.2_Range_Finder.py`, `2c_Exercise_0.3_Ear_Training.py`
- Level 1: `3_Exercise_1.1_Diaphragmatic_Support.py` → `8_Exercise_1.6_Staccato_vs_Legato.py`
- Level 2: `9_Exercise_2.1_Major_Scale_Ascending.py` → `14_Exercise_2.6_Pitch_Stability.py`

**Benefits:**

- Consistent ordering in Streamlit sidebar (Streamlit uses alphabetical + numeric sorting)
- Clear visual hierarchy (level progression obvious from filenames)
- Easy to identify exercise type and level at a glance
- Simple to add new exercises (increment order number)

## 📋 Exercise Library

### Level 0: Diagnostics & Placement
1. **0.1 Warm-Up Recording** — 3-note pattern to assess baseline tone/breath
2. **0.2 Range Finder** — Ascending/descending scale to detect voice type
3. **0.3 Ear Training** — 3 pitch-matching tasks for placement routing

**Output:** Voice profile (range, voice type) + placement level (1 or 2)

### Level 1: Breath & Tone Fundamentals
1. **1.1 Diaphragmatic Support** — Sustain "sss" sound; measure breath consistency
2. **1.2 Silent Breath Control** — Controlled breathing without phonation
3. **1.3 Smooth Onset** — Attack without harshness
4. **1.4 Legato** — Connected singing on 3-note patterns
5. **1.5 Five-Note Scale** — Scale accuracy and breath control
6. **1.6 Staccato vs Legato** — Articulation contrast

**Metrics:** Duration, stability, control, tone quality

### Level 2: Pitch, Scales & Ears
1. **2.1 Major Scale Ascending** — 3 scales at different starting pitches
2. **2.2 Major Scale Descending** — Pitch control going down + sagging detection
3. **2.3 Minor Scales** — Natural minor (♭3, ♭6, ♭7) accuracy
4. **2.4 Interval Training** — Major 3rd, 4th, 5th, 6th, octave matching
5. **2.5 Arpeggios** — Vertical leaps on major triads; cracks detection
6. **2.6 Pitch Stability Game** — Sustain single note 6-8s with real-time gauge

**Metrics:** Pitch accuracy (cents), sagging %, stability, volume consistency, in-target %

## 🏗️ Architecture

### Page Management System (v2.0)

The app uses a **centralized configuration system** (`utils/pages_config.py`) with standardized components:

**Benefits:**

-  Single source of truth for all page metadata
-  Easy to add new levels/exercises (just add one entry)
-  Automatic progress tracking and unlock logic
-  Consistent navigation across the app
-  Unified naming convention for all pages

**Example metadata entry:**

```python
"3_Exercise_1.1_Diaphragmatic_Support": {
    "level": 1,
    "title": "💨 1.1 Diaphragmatic Support",
    "description": "Master breath control and consistency",
    "skills": ["Breath Support", "Stability", "Control"],
    "difficulty": "Beginner",
    "duration_minutes": 8,
    "prerequisites": ["Level 0"],
}
```

**Configuration Functions:**

- `get_page_info()` — Retrieve metadata for any page
- `get_pages_by_level()` — Get all exercises in a level
- `get_level_progress()` — Calculate completion % for each level
- `is_page_unlocked()` — Check lock status based on prerequisites & placement
- `get_sidebar_display_name()` — Standardized display formatting
- `get_level_badge()` — Level emoji badges (🎯/📚/⭐)

**Enhanced Sidebar Component:**

- `render_enhanced_sidebar()` — Shows progress metrics, quick navigation, focus areas
- `render_page_header()` — Standard page header with metadata display
- Real-time progress visualization with completion percentages
- Lock/unlock icons for exercise access control
- Difficulty indicators (🟢 Beginner, 🟡 Intermediate, 🔴 Advanced)

```
ai_vocal_coach/
├── analysis/
│   └── audio_processor.py        # YIN pitch detection, metrics extraction
├── engine/
│   ├── feedback.py               # Exercise evaluators (all levels)
│   └── placement.py              # Voice type classifier, placement logic
├── visualization/
│   └── charts.py                 # Plotly wrappers (pitch tracking, gauges, radars)
├── components/
│   ├── ui.py                     # Streamlit UI blocks + CSS styling
│   └── sidebar.py                # Enhanced sidebar with progress & navigation
├── utils/
│   ├── state.py                  # Session state + voice profile schema
│   ├── file_handler.py           # Audio file I/O
│   └── pages_config.py           # Centralized page metadata & config system
├── pages/
│   ├── 1_Dashboard.py            # Progress overview & hub
│   ├── 2a_Exercise_0.1_Warm_Up.py
│   ├── 2b_Exercise_0.2_Range_Finder.py
│   ├── 2c_Exercise_0.3_Ear_Training.py
│   ├── 3-8_Exercise_1.X_*.py    # Level 1 exercises (6 files)
│   └── 9-14_Exercise_2.X_*.py   # Level 2 exercises (6 files)
└── app.py                        # Dashboard entry point
```

## 🚀 Local Setup

```bash
# Clone repo
git clone <repo-url>
cd ai-vocal-coach

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run ai_vocal_coach/app.py
```

## 📦 Dependencies
- **streamlit** (>=1.37.0) — Web UI framework
- **numpy** (>=1.26.4) — Array operations, pitch metrics
- **plotly** (>=5.22.0) — Interactive visualizations
- **pandas** (>=2.2.2) — Data handling

## 🎯 User Flow

1. **Start → Level 0** (Diagnostics)
   - Warm-up + range detection + ear training
   - System classifies voice type and selects starting level

2. **Level 1** (Fundamentals)
   - 6 breath/tone exercises with feedback
   - Unlock Level 2 after completion (or skip if placed high)

3. **Level 2** (Advanced)
   - 6 pitch/scale exercises with real-time analytics
   - Track XP, best scores, and overall progress

4. **Dashboard** (Progress Hub)
   - View vocal profile, level completion, XP/scores
   - See personalized focus areas
   - Track improvement over time

## 🎨 UI/UX Enhancements

### Theme System

**Light & Dark Mode Support:**
- Click the theme toggle button (☀️/🌙) in the sidebar to switch themes
- Theme preference persists throughout your session
- Both themes optimized for readability and visual appeal

**Color Schemes:**

**Dark Theme (Default):**
- **Primary:** #00D26A (vibrant green)
- **Secondary:** #7c3aed (purple)
- **Accent:** #FF6B9D (pink)
- **Success:** #28a745 (green gradients)
- **Warning:** #ffc107 (orange gradients)
- **Background:** #0e1419 (dark slate)

**Light Theme:**

- Same accent colors with adjusted backgrounds
- White background (#ffffff) for clarity
- Adjusted contrast for readability
- Lighter card backgrounds for visual hierarchy

### Components

- **Hero Card:** Gradient-filled profile header with blur effects
- **Metric Cards:** Hover animations, gradient backgrounds, shadow effects
- **Badges:** Gradient fills for score ranges (excellent/good/try-again)
- **Exercise Cards:** Left border accent, hover lift effect
- **Instruction Boxes:** Color-coded left border with semi-transparent backgrounds
- **Charts:** Rounded containers with shadow depth, enhanced hover states

### Interactive Elements
- **Buttons:** Gradient background, elevation on hover, smooth transitions
- **Alert Boxes:** Themed left border, semi-transparent backgrounds
- **Plotly Charts:** Dark theme, grid backgrounds, smooth animations

## 📊 Feedback System

All exercises return standardized output:
```python
(overall_score: int, feedback_list: list, subscores: dict)
```

### Example
```python
score = 85
feedback = [
    "✅ Excellent pitch accuracy! Notes are right on target.",
    "⚠️ Slight sagging on the higher notes. Maintain breath support."
]
subscores = {
    "Pitch Accuracy": 88,
    "No Sagging": 82,
    "Stability": 85
}
```

## 🔬 Vocal Analysis Metrics

### Pitch Metrics
- **Accuracy (cents):** Deviation from target pitch (±50 cents = good)
- **Sagging %:** Percentage of frames below target (lower is better)
- **Drift (Hz):** Pitch variation during sustained notes
- **In-Target %:** Time spent within tolerance band

### Breath Metrics
- **Stability:** RMS consistency (0-1 scale, higher is better)
- **Consistency:** Breath/volume fluctuation analysis
- **Duration:** Phonation length in seconds

### Tone Metrics
- **Breathiness (ZCR):** High-frequency energy (lower = clearer)
- **Register Breaks:** Detected jumps/cracks in frequency

## 🎓 Next Steps (Future)

- **Level 3:** Articulation & vowel modification
- **Recording Library:** Save and compare exercise takes
- **Peer Comparison:** Benchmark scores against similar voice types
- **Mobile App:** React Native companion for iOS/Android
- **Offline Mode:** Record → analyze → upload workflow

## 💾 Data Storage

- Session-based state in Streamlit session cache
- Voice profiles stored in session JSON schema
- Exercise scores and XP in in-memory history
- Ready for database migration (PostgreSQL, Firebase, etc.)

## 🐛 Troubleshooting

**No pitch detected?**
- Sing louder and clearer
- Use a single sustained vowel (not consonants)
- Ensure good microphone input levels

**Scale feedback inaccurate?**
- Sustain each note for 1-2 seconds
- Keep volume consistent across all notes
- Avoid vibrato on beginning exercises

**App won't start?**
- Check Python version (3.8+)
- Verify all dependencies: `pip install -r requirements.txt`
- Clear Streamlit cache: `streamlit cache clear`

## 📈 What's Been Built

### ✅ Complete Implementation (15 Exercises)

#### Level 0 — Diagnostics (3 exercises)

- Warm-up recording analysis
- Vocal range detection + voice type classification
- Pitch-matching ear training
- Automatic placement routing (Level 1 or 2)

#### Level 1 — Breath & Tone Fundamentals (6 exercises)

- Diaphragmatic support basics
- Silent breath control
- Smooth onset technique
- Legato singing
- Five-note scale accuracy
- Staccato vs legato contrast

#### Level 2 — Pitch, Scales & Ears (6 exercises)

- Major scale ascending (3 starting pitches)
- Major scale descending with sagging detection
- Natural minor scales (♭3, ♭6, ♭7 accuracy)
- Interval training (major 3rd through octave)
- Arpeggios with leap accuracy + crack detection
- Pitch stability game (6-8 second holds with real-time gauge)

### 🔧 Technical Stack

#### Analysis Engine

- YIN pitch detection (autocorrelation)
- 8 advanced metric functions (accuracy, sagging, drift, etc.)
- 12 standardized evaluators (Level 0, 1, 2)
- Voice type classifier (6 voice types)
- Placement routing logic

#### Visualization (Plotly)

- Waveform plots with area fill
- Pitch contour tracking
- Pitch vs target overlay comparison
- Real-time stability gauges (dual meter)
- Radar charts for multi-dimensional scoring
- Dark theme optimization

#### UI/UX (Streamlit + Custom CSS)

- 80+ CSS style rules
- Gradient color scheme (green/purple/pink)
- Hover animations and transitions
- Responsive mobile design
- Accessibility standards (WCAG)
- Score badges, instruction boxes, alert boxes
- Tone synthesis (numpy + wave)

## 📄 License

MIT License — See LICENSE file for details

## 🤝 Contributing

Contributions welcome! Please submit PRs with:
- Feature description and motivation
- Test results and verification
- Updated documentation
- Screenshots of UI changes (if applicable)

### Future Enhancement Ideas
- **Level 3:** Articulation & vowel modification
- **Recording Library:** Save and compare exercise takes
- **Peer Benchmarking:** Compare scores against similar voice types
- **Mobile App:** React Native companion
- **Database:** PostgreSQL integration for progress persistence
- **Social:** Share achievements and scores

## 📚 References

**Pitch Detection Algorithm:**
- YIN: A Fundamental Frequency Estimator for Speech and Music (de Cheveigné & Kawahara, 2002)

**Vocal Science:**
- Standard operatic vocal ranges and classifications
- Natural minor scale structure (W-H-W-W-H-W-W)
- Register break detection and analysis

**UI/UX Principles:**
- Material Design 3 color system
- Gradient design best practices
- Accessibility (WCAG 2.1 AA)

---

## 🚀 Getting Started

```bash
# Clone repository
git clone <repo-url>
cd ai-vocal-coach

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run application
streamlit run ai_vocal_coach/app.py

# Open browser to http://localhost:8501
```

## 💡 Tips for Best Results

**For Accurate Analysis:**
1. Use a quiet room with minimal background noise
2. Sing clearly and confidently
3. Sustain notes for 1-2 seconds (longer = better data)
4. Use single vowels (ah, oh, eh) without consonants
5. Avoid vibrato on fundamental exercises
6. Keep volume consistent across all notes

**For Better Learning:**
1. Start with Level 0 to establish baseline
2. Complete Level 1 before advancing to Level 2
3. Practice multiple times to see improvement
4. Read all feedback and focus areas
5. Use reference tones to calibrate your ear
6. Track progress on the dashboard

---

**Happy singing! 🎵**

Use AI Vocal Coach daily to improve:
- **Tone quality** and resonance
- **Pitch accuracy** and intonation
- **Breath support** and control
- **Vocal stamina** and consistency
- **Overall confidence** as a singer

---

**Version:** 1.0.0 | **Last Updated:** July 2026 | **Status:** Production Ready 
