"""Five vowel rounds with vowel-envelope analysis and shared final results."""
import io
import hashlib
from pathlib import Path
import sys
import numpy as np
import soundfile as sf
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.exercise_flow import (
    init_exercise_flow, reset_for_new_exercise, render_stage_indicator,
    render_introduction_stage, recording_input, move_to_results, render_results_stage,
)
from components.ui import inject_custom_css, render_top_nav
from engine.audio_analysis import analyze_audio
from utils.audio_generator import generate_tone
from utils.exercise_models import get_profile
from utils.pages_config import get_page_info
from utils.state import init_session_state

EXERCISE_ID = "15_Exercise_3.1_Pure_Italian_Vowels"
NEXT_PAGE = "pages/16_Exercise_3.2_Vowel_Consistency_Ascending.py"
VOWELS = [("A", "Open the mouth; keep the tongue low."), ("E", "Use a clear eh without moving to ee."),
          ("I", "Keep the pure ee steady."), ("O", "Keep the lips rounded."), ("U", "Keep oo rounded and free.")]


def combine_rounds(rounds):
    names = set().union(*(r["result"]["subscores"] for r in rounds))
    scores = {name: int(round(np.mean([r["result"]["subscores"][name] for r in rounds if name in r["result"]["subscores"]]))) for name in sorted(names)}
    events = []
    offset = 0.0
    for r in rounds:
        for item in r["result"]["feedback"]:
            seconds = offset + r["result"].get("analysis_meta", {}).get("onset_offset_seconds", 0) + item.get("seconds", 0)
            events.append({**item, "seconds":seconds, "time":f"{int(seconds)//60}:{seconds%60:04.1f}", "round":r["vowel"], "message":f"Vowel {r['vowel']}: {item['message']}"})
        offset += r["result"]["duration"]
    durations = [r["result"]["performance_duration"] for r in rounds]
    if np.std(durations)/max(np.mean(durations), .1) > .2:
        events.append({"time":"", "seconds":0, "message":"Some vowels were held longer than others — aim for the same length each time.", "valence":"negative", "rule":"uneven_vowel_duration", "timing":"Summary"})
    buffers = []
    for r in rounds:
        y, sr = sf.read(io.BytesIO(r["audio"]), always_2d=True)
        if sr != 16000:
            import librosa
            y = librosa.resample(y.mean(axis=1), orig_sr=sr, target_sr=16000)[:,None]
        buffers.append(y.mean(axis=1))
    combined = io.BytesIO()
    sf.write(combined, np.concatenate(buffers), 16000, format="WAV")
    score = int(round(np.mean(list(scores.values())))) if scores else 0
    complete = len(rounds)==5 and all(r["result"]["complete"] for r in rounds)
    return {"score":score, "xp":int(score*.6) if complete else 0, "subscores":scores, "feedback":events,
            "complete":complete, "duration":sum(r["result"]["duration"] for r in rounds),
            "metric_evidence":{name:{"explanation":"Mean of the measured scores across completed vowel rounds."} for name in scores},
            "performance_duration":sum(durations), "pitch_data":{}, "analysis_meta":{"onset_offset_seconds":0}}, combined.getvalue()


init_session_state()
inject_custom_css()
render_top_nav("exercise")
init_exercise_flow()
reset_for_new_exercise(EXERCISE_ID)
render_stage_indicator(st.session_state.exercise_stage)

if st.session_state.exercise_stage == "introduction":
    render_introduction_stage(get_page_info(EXERCISE_ID))
elif st.session_state.exercise_stage == "recording":
    rounds = st.session_state.setdefault("vowel_results", [])
    index = len(rounds)
    vowel, tip = VOWELS[index]
    st.markdown(f"### Round {index+1} of 5 · {vowel}")
    st.info(tip + " Hold for 3–4 seconds without changing the vowel.")
    selection = st.selectbox("Comfortable reference", ["C4", "A3", "A4"], key="vowel_reference")
    reference = {"C4":261.6256, "A3":220., "A4":440.}[selection]
    profile = get_profile("3.1")
    profile["rounds"] = [vowel]
    st.audio(generate_tone(reference, 2), sample_rate=16000)
    audio, context = recording_input(EXERCISE_ID, profile, reference, suffix=f"vowel_{index}")
    if audio:
        signature = (hashlib.sha256(audio).hexdigest(), reference)
        if st.button("Analyse this vowel", key=f"vowel_analyse_{index}"):
            context.update({"vowel":vowel, "reference_hz":reference})
            with st.spinner("Analysing pitch and vowel envelope…"):
                result = analyze_audio(audio, "vowel_sustain", context)
            st.session_state[f"vowel_result_{index}"] = {"signature": signature, "analysis": result}
        cached = st.session_state.get(f"vowel_result_{index}", {})
        result = cached.get("analysis") if cached.get("signature") == signature else None
        if result:
            st.write(f"Measured skills: {result['score']}/100")
            for item in result["feedback"]:
                st.write(item["message"])
            if st.button("Next vowel" if index<4 else "View all results", key=f"vowel_next_{index}", disabled=not result["complete"]):
                rounds.append({"vowel":vowel, "result":result, "audio":audio})
                if len(rounds)==5:
                    analysis, combined = combine_rounds(rounds)
                    st.session_state.exercise_analysis = analysis
                    st.session_state.recorded_audio = combined
                    move_to_results()
                st.rerun()
elif st.session_state.exercise_stage == "results":
    render_results_stage(EXERCISE_ID, NEXT_PAGE)
