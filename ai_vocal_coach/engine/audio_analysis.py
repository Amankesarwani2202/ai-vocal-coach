"""Public audio-analysis API backed by the exercise-aware signal engine."""
import io
import wave as _wave
import numpy as np
from utils.exercise_models import get_profile


def exercise_type_from_id(exercise_id):
    return get_profile(exercise_id)["type"]


def pitch_movement_expected(exercise_type):
    return get_profile(exercise_type)["pitch_model"] in {"stepped", "glide"}


def analyze_audio(audio_bytes, exercise_type="warm_up", context=None):
    from engine.exercise_analysis import analyze_exercise
    return analyze_exercise(audio_bytes, exercise_type, context)


def analyze_rhythm_timing(audio_bytes, bpm=80, beats_per_bar=4, total_bars=4,
                          exercise_type="metronome_singing", context=None):
    settings = dict(context or {})
    settings["bpm"] = bpm
    return analyze_audio(audio_bytes, exercise_type, settings)


def analyze_pitch_match(audio_bytes, reference_hz):
    """Ear-training API: compare a clear sung note, permitting an octave match."""
    from engine.exercise_analysis import extract_features
    empty={"cents_deviation":None,"abs_cents":None,"quality":"no_audio","sung_hz":None,"score":0}
    if not audio_bytes or not (50 <= reference_hz <= 2000):
        return empty
    try:
        features=extract_features(audio_bytes)
    except (ValueError,RuntimeError):
        return empty
    if features.duration < .8:
        return {**empty,"quality":"too_short"}
    values=features.f0[features.voiced]
    if len(values)<6:
        return {**empty,"quality":"no_pitch"}
    sung_hz=float(np.median(values))
    best=min((sung_hz,sung_hz*2,sung_hz*.5),key=lambda hz:abs(1200*np.log2(hz/reference_hz)))
    deviation=float(1200*np.log2(best/reference_hz));error=abs(deviation)
    quality="excellent" if error<=15 else "good" if error<=30 else "fair" if error<=50 else "off" if error<=100 else "miss"
    score=int(np.interp(error,[0,15,30,50,100,200],[100,88,74,55,28,0]))
    return {"cents_deviation":round(deviation,1),"abs_cents":round(error,1),"quality":quality,"sung_hz":round(sung_hz,1),"score":score}


def generate_click_track(bpm=80, bars=4, beats_per_bar=4, sr=16000):
    """Generate a metronome click track as WAV bytes."""
    beat_interval = 60.0 / max(bpm, 20)
    total_samples = int(sr * bars * beats_per_bar * beat_interval) + sr
    audio = np.zeros(total_samples, dtype=np.float32)
    click_samples = int(sr * 0.04)
    for bar in range(bars):
        for beat in range(beats_per_bar):
            start = int((bar * beats_per_bar + beat) * beat_interval * sr)
            freq = 1000.0 if beat == 0 else 750.0
            tc = np.linspace(0, 0.04, click_samples, endpoint=False)
            click = (np.sin(2 * np.pi * freq * tc) * np.exp(-tc * 50) * 0.6).astype(np.float32)
            end = min(start + click_samples, total_samples)
            audio[start:end] += click[:end - start]
    audio = np.clip(audio, -1.0, 1.0)
    buf = io.BytesIO()
    with _wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(
            np.clip(audio * 32767, -32767, 32767).astype(np.int16).tobytes()
        )
    buf.seek(0)
    return buf.getvalue()
