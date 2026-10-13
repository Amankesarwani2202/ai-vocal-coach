# AI Vocal Coach

Streamlit vocal exercises with recorded-audio analysis, measured feedback and progress tracking. The active curriculum contains 41 exercises across levels 0–7.

## Run locally

```bash
pip install -r ai_vocal_coach/requirements.txt
cd ai_vocal_coach
streamlit run app.py
```

Use the simple microphone or the optional recorder with live visual cues. Microphone permission is requested when recording starts. Analysis runs locally in the application after capture; the custom recorder has no external dependencies.

## Analysis and curriculum

- `assets/curriculum.json` defines note durations, pitch models, articulation sections and rhythm grids.
- `engine/exercise_analysis.py` extracts pitch, energy, spectral and vowel features and applies exercise-specific rules.
- `engine/audio_analysis.py` preserves the public analysis and ear-training API.
- `components/exercise_flow.py` shares introduction, recording, charts, coaching and completion behavior.
- Supplied instrumental references and notation are in `assets/examples` and `assets/scores`. Generated references use the same note definitions as analysis.

Pitch targets are relative to the first confirmed note unless a reference is selected. Rhythm exercises use discrete grids and unique attack matching; absolute offbeat phase requires a shared recorder clock. Physiological placement, projection and uncalibrated word-level diction claims are withheld. See [QA_REQUIREMENTS.md](QA_REQUIREMENTS.md) for source discrepancies, requirement coverage and measurement limits.

## Verification

```bash
pip install pytest
python -m pytest -q
```

Tests cover controlled audio signals, scoring/coaching regressions, media/catalog integrity and every active Streamlit exercise page. A real-device microphone smoke test remains necessary before merging. Publishing this branch does not update the deployed Streamlit app; deployment follows its configured branch after merge.
