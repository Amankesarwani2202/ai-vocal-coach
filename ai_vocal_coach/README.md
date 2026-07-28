# AI Vocal Coach

A simple Streamlit-based vocal coaching prototype for practicing breath support and tone control exercises.

## Setup

```bash
cd ai_vocal_coach
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Structure

- `app.py` launches the main dashboard and navigation.
- `pages/` contains the guided exercises.
- `analysis/`, `engine/`, `components/`, `utils/`, and `visualization/` house the app logic.
