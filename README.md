# AI Vocal Coach 🎤

An AI-powered singing practice application that analyzes a singer's voice in real-time and provides feedback similar to a personal vocal coach. Built natively on Streamlit.

## Features
- **Browser-Native Recording:** No extensions, no Docker, no external APIs.
- **Real-Time Analysis:** Uses `librosa` for pitch detection (YIN), amplitude envelope, and stability metrics.
- **Rule-Based AI Engine:** Gives actionable feedback based on acoustic features.
- **Gamified Tracking:** XP system, dynamic radar charts, and progress dashboards.

## Architecture
- `analysis/`: Signal processing (Librosa, SoundFile)
- `engine/`: AI feedback logic and scoring thresholds
- `visualization/`: Plotly wrappers for rendering acoustic data
- `components/`: UI/UX Streamlit blocks
- `pages/`: Independent exercise modules

## Local Setup
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py