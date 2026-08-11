"""
Real-time vocal analysis engine using librosa.
Analyses pitch stability, breath support, onset smoothness, and continuity
for each exercise type. Returns structured feedback_data suitable for
render_results_stage().
"""

import io
import wave as _wave
import numpy as np

try:
    import librosa
    import librosa.feature
    import librosa.onset
    LIBROSA_OK = True
except ImportError:
    LIBROSA_OK = False

HOP = 512
FRAME = 2048


# ── Loading ──────────────────────────────────────────────────────────────────

def _load_audio(audio_bytes):
    """Return (y float32 mono, sr) from WAV bytes. Tries librosa then wave."""
    if LIBROSA_OK:
        try:
            y, sr = librosa.load(io.BytesIO(audio_bytes), sr=None, mono=True)
            return y.astype(np.float32), int(sr)
        except Exception:
            pass
    # Fallback: manual WAV parse
    try:
        with _wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            ch = wf.getnchannels()
            sw = wf.getsampwidth()
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())
        dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw, np.int16)
        raw = np.frombuffer(frames, dtype=dtype).astype(np.float32)
        if ch > 1:
            raw = raw.reshape(-1, ch).mean(axis=1)
        y = raw / float(np.iinfo(dtype).max)
        return y, sr
    except Exception:
        return None, None


# ── Feature extraction ────────────────────────────────────────────────────────

def _pitch_track_fallback(y, sr):
    """YIN-inspired pitch detection — no numba required."""
    fmin, fmax = 65.0, 1050.0
    min_period = max(2, int(sr / fmax))
    max_period = min(FRAME // 2, int(sr / fmin))

    f0_list, vf_list = [], []
    win = np.hanning(FRAME)

    for start in range(0, len(y) - FRAME + 1, HOP):
        frame = y[start: start + FRAME]
        frame = frame - frame.mean()           # zero-mean
        energy = float(np.dot(frame, frame))
        if energy < 1e-9:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        frame_w = frame * win

        # Normalized autocorrelation
        corr = np.correlate(frame_w, frame_w, mode="full")[FRAME - 1:]
        corr_norm = corr / (corr[0] + 1e-10)

        # YIN difference function d[tau] = 2*r[0] - 2*r[tau]
        # Cumulative mean normalised difference for voiced/unvoiced decision
        d = 2.0 * (corr_norm[0] - corr_norm[min_period: max_period + 1])
        if len(d) == 0:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        # Cumulative mean normalisation
        cum = np.cumsum(d)
        idx = np.arange(1, len(d) + 1)
        cmnd = np.where(idx > 0, d * idx / (cum + 1e-10), 1.0)

        # Find first dip below threshold
        threshold = 0.18
        dip_candidates = np.where(cmnd < threshold)[0]
        if len(dip_candidates) > 0:
            tau = int(dip_candidates[0]) + min_period
        else:
            tau = int(np.argmin(cmnd)) + min_period

        # Parabolic interpolation for sub-sample accuracy
        if 0 < tau < len(corr_norm) - 1:
            a, b, c = corr_norm[tau - 1], corr_norm[tau], corr_norm[tau + 1]
            denom = 2.0 * (2 * b - a - c)
            refined = tau + (c - a) / (denom + 1e-10) if abs(denom) > 1e-6 else tau
        else:
            refined = tau

        voiced = len(dip_candidates) > 0 or float(np.min(cmnd)) < 0.30
        if voiced and refined > 0:
            f0_list.append(sr / max(refined, 1.0))
            vf_list.append(True)
        else:
            f0_list.append(np.nan)
            vf_list.append(False)

    if not f0_list:
        n = len(y) // HOP + 1
        return np.full(n, np.nan), np.zeros(n, dtype=bool)

    f0 = np.array(f0_list, dtype=np.float64)
    vf = np.array(vf_list, dtype=bool)

    # 3-point median smoothing on voiced runs to suppress octave errors
    for i in range(1, len(f0) - 1):
        if vf[i - 1] and vf[i] and vf[i + 1]:
            f0[i] = float(np.median([f0[i - 1], f0[i], f0[i + 1]]))

    return f0, vf


def _pitch_track(y, sr):
    """Return (f0_hz, voiced_flag) at HOP intervals using pyin, with fallback."""
    if LIBROSA_OK:
        try:
            f0, vf, _ = librosa.pyin(
                y,
                fmin=librosa.note_to_hz("C2"),
                fmax=librosa.note_to_hz("C7"),
                sr=sr,
                hop_length=HOP,
            )
            f0 = np.where(vf, f0, np.nan)
            return f0, vf.astype(bool)
        except Exception:
            pass
    return _pitch_track_fallback(y, sr)


def _rms_track(y):
    """Return RMS energy array at HOP intervals."""
    if LIBROSA_OK:
        try:
            return librosa.feature.rms(y=y, frame_length=FRAME, hop_length=HOP)[0]
        except Exception:
            pass
    n = len(y) // HOP + 1
    out = np.zeros(n)
    for i in range(n):
        seg = y[i * HOP: i * HOP + FRAME]
        out[i] = float(np.sqrt(np.mean(seg ** 2))) if len(seg) else 0.0
    return out


def _frames_to_time(n, sr):
    if LIBROSA_OK:
        return librosa.frames_to_time(np.arange(n), sr=sr, hop_length=HOP)
    return np.arange(n) * HOP / sr


# ── Scoring primitives ────────────────────────────────────────────────────────

def _pitch_stability(f0):
    voiced = f0[~np.isnan(f0)]
    if len(voiced) < 5:
        return 50
    window = max(10, int(len(voiced) // 5))
    stds = []
    for i in range(0, len(voiced), window):
        seg = voiced[i: i + window]
        if len(seg) < 3:
            continue
        med = np.nanmedian(seg)
        if med < 1:
            continue
        cents = 1200 * np.log2(np.clip(seg / med, 1e-6, None))
        stds.append(float(np.std(cents)))
    if not stds:
        return 50
    mean_std = float(np.mean(stds))
    # ≤10 cents → 95, 60 cents → 40
    return int(np.clip(np.interp(mean_std, [0, 10, 30, 60, 100], [97, 90, 70, 45, 25]), 0, 100))


def _breath_support(rms, voiced_flag):
    n = min(len(rms), len(voiced_flag))
    vr = rms[:n][voiced_flag[:n]]
    if len(vr) < 3:
        return 65
    cv = float(np.std(vr)) / (float(np.mean(vr)) + 1e-9)
    return int(np.clip(np.interp(cv, [0, 0.1, 0.25, 0.45, 0.7], [95, 88, 70, 50, 28]), 0, 100))


def _continuity(voiced_flag):
    if len(voiced_flag) == 0:
        return 50
    gaps = int(np.sum(np.diff(voiced_flag.astype(int)) == -1))
    rate = gaps / max(len(voiced_flag), 1)
    return int(np.clip(np.interp(rate, [0, 0.02, 0.05, 0.12, 0.25], [96, 85, 65, 45, 22]), 0, 100))


def _onset_smoothness(y, sr):
    if not LIBROSA_OK:
        return 70
    try:
        frames = librosa.onset.onset_detect(y=y, sr=sr, hop_length=HOP)
        rms = _rms_track(y)
        scores = []
        for of in frames:
            pre = float(np.mean(rms[max(0, of - 6): of])) if of > 0 else 0.0
            post = float(np.mean(rms[of: of + 6])) if of < len(rms) else 0.0
            if post < 1e-7:
                continue
            rise = (post - pre) / post  # 0=gradual, 1=abrupt
            scores.append(rise)
        if not scores:
            return 72
        mean_rise = float(np.mean(scores))
        return int(np.clip(np.interp(mean_rise, [0, 0.3, 0.6, 0.85, 1.0], [95, 85, 65, 45, 28]), 0, 100))
    except Exception:
        return 70


def _voiced_pct(voiced_flag):
    if len(voiced_flag) == 0:
        return 0.0
    return float(np.sum(voiced_flag)) / len(voiced_flag)


# ── Per-exercise subscores ────────────────────────────────────────────────────

_WEIGHTS = {
    "warm_up":          [0.40, 0.35, 0.25],
    "range_finder":     [0.45, 0.30, 0.25],
    "ear_training":     [0.55, 0.25, 0.20],
    "breath_support":   [0.15, 0.55, 0.30],
    "silent_breath":    [0.20, 0.50, 0.30],
    "smooth_onset":     [0.20, 0.55, 0.25],
    "legato":           [0.25, 0.30, 0.45],
    "scale":            [0.55, 0.25, 0.20],
    "staccato":         [0.30, 0.25, 0.45],
    "scale_ascending":  [0.55, 0.25, 0.20],
    "scale_descending": [0.55, 0.25, 0.20],
    "minor_scale":      [0.55, 0.25, 0.20],
    "intervals":        [0.60, 0.20, 0.20],
    "arpeggios":        [0.55, 0.20, 0.25],
    "pitch_stability":  [0.65, 0.20, 0.15],
}


def _subscores(y, sr, f0, voiced_flag, rms, exercise_type):
    ps  = _pitch_stability(f0)
    bs  = _breath_support(rms, voiced_flag)
    con = _continuity(voiced_flag)
    ons = _onset_smoothness(y, sr)
    prs = min(100, int(_voiced_pct(voiced_flag) * 130))

    table = {
        "warm_up":          {"Pitch Stability": ps,   "Breath Support": bs,   "Consistency": con},
        "range_finder":     {"Range Clarity": ps,     "Voice Presence": prs,  "Transitions": con},
        "ear_training":     {"Pitch Accuracy": ps,    "Intonation": ps,       "Voice Presence": prs},
        "breath_support":   {"Airflow Steadiness": bs,"Support Duration": con,"Consistency": bs},
        "silent_breath":    {"Breath Control": bs,    "Support Duration": con,"Consistency": bs},
        "smooth_onset":     {"Attack Smoothness": ons,"Consistency": ps,      "Tone Quality": bs},
        "legato":           {"Continuity": con,       "Phrase Shape": ps,     "Onset Smoothness": ons},
        "scale":            {"Pitch Accuracy": ps,    "Evenness": bs,         "Smoothness": ons},
        "staccato":         {"Articulation": ons,     "Pitch Accuracy": ps,   "Consistency": bs},
        "scale_ascending":  {"Pitch Accuracy": ps,    "Evenness": bs,         "Range": prs},
        "scale_descending": {"Pitch Accuracy": ps,    "Control": bs,          "Consistency": con},
        "minor_scale":      {"Pitch Accuracy": ps,    "Tone Quality": bs,     "Consistency": con},
        "intervals":        {"Interval Accuracy": ps, "Intonation": ps,       "Confidence": prs},
        "arpeggios":        {"Pitch Accuracy": ps,    "Agility": ons,         "Consistency": con},
        "pitch_stability":  {"Pitch Stability": ps,   "Vibrato Control": max(0, ps - 8), "Sustain": con},
    }
    return table.get(exercise_type, {"Pitch Stability": ps, "Breath Support": bs, "Consistency": con})


def _weighted_score(sub, exercise_type):
    vals  = list(sub.values())
    ws    = _WEIGHTS.get(exercise_type, [1 / len(vals)] * len(vals))
    if len(ws) != len(vals):
        ws = [1 / len(vals)] * len(vals)
    raw = sum(v * w for v, w in zip(vals, ws))
    return int(np.clip(raw, 30, 100))


def _xp(score):
    if score >= 90: return 150
    if score >= 80: return 120
    if score >= 70: return 100
    if score >= 60: return 80
    return 50


# ── Feedback generation ───────────────────────────────────────────────────────

def _ts(sec):
    return f"{int(sec // 60)}:{int(sec % 60):02d}"


def _range_notes(f0):
    if not LIBROSA_OK:
        return None, None
    voiced = f0[~np.isnan(f0)]
    if len(voiced) < 5:
        return None, None
    try:
        low  = librosa.hz_to_note(float(np.percentile(voiced, 5)),  octave=True)
        high = librosa.hz_to_note(float(np.percentile(voiced, 95)), octave=True)
        return low, high
    except Exception:
        return None, None


def _generate_feedback(y, sr, f0, voiced_flag, rms, times, exercise_type, duration):
    fb = []
    n = min(len(f0), len(voiced_flag), len(rms), len(times))
    f0, voiced_flag, rms, times = f0[:n], voiced_flag[:n], rms[:n], times[:n]

    # Opening note: centre pitch
    all_voiced = f0[voiced_flag & ~np.isnan(f0)]
    if len(all_voiced) >= 8 and LIBROSA_OK:
        try:
            note = librosa.hz_to_note(float(np.nanmedian(all_voiced)), octave=True)
            fb.append({"time": "0:00", "message": f"Pitch centres around {note}"})
        except Exception:
            pass

    # Windowed analysis (~2 s segments)
    win = max(1, int(2.0 * sr / HOP))
    prev_rms_mean = None

    for w in range(0, n, win):
        e = min(w + win, n)
        if e - w < 4:
            continue
        mid = float(times[w + (e - w) // 2])
        seg_f0 = f0[w:e]
        seg_vf = voiced_flag[w:e]
        seg_rms = rms[w:e]
        voiced_f0 = seg_f0[seg_vf & ~np.isnan(seg_f0)]
        voiced_rms = seg_rms[seg_vf]
        rms_mean = float(np.mean(seg_rms))
        voiced_pct = float(np.sum(seg_vf)) / (e - w)

        # Pitch stability in window
        if len(voiced_f0) >= 5:
            med = float(np.nanmedian(voiced_f0))
            if med > 1:
                cents = 1200 * np.log2(np.clip(voiced_f0 / med, 1e-6, None))
                std_c = float(np.std(cents))
                if std_c > 65:
                    fb.append({"time": _ts(mid), "message": "Pitch wavering — focus on a fixed target"})
                elif std_c > 35:
                    fb.append({"time": _ts(mid), "message": "Some pitch drift — try to lock in the note"})
                elif std_c < 15 and len(voiced_f0) >= 12:
                    fb.append({"time": _ts(mid), "message": "Clean, steady pitch here"})

        # Breath support drop
        if prev_rms_mean is not None and rms_mean < prev_rms_mean * 0.50 and voiced_pct > 0.3:
            fb.append({"time": _ts(mid), "message": "Breath support fading — push from the diaphragm"})

        # Gap / silence mid-phrase
        if voiced_pct < 0.15 and mid < duration * 0.85:
            fb.append({"time": _ts(mid), "message": "Gap detected — try to sustain through the phrase"})

        # Choppy airflow
        if len(voiced_rms) > 4:
            cv = float(np.std(voiced_rms)) / (float(np.mean(voiced_rms)) + 1e-9)
            if cv > 0.55:
                fb.append({"time": _ts(mid), "message": "Airflow uneven — aim for a smooth, steady stream"})

        prev_rms_mean = rms_mean

    # Range detection for range finder exercise
    if exercise_type == "range_finder":
        low, high = _range_notes(f0)
        if low and high:
            fb.append({"time": _ts(duration * 0.9), "message": f"Detected range: {low} – {high}"})

    # Deduplicate by message prefix and cap at 8
    seen, out = set(), []
    for item in fb:
        key = item["message"][:35]
        if key not in seen:
            seen.add(key)
            out.append(item)
    return out[:8]


# ── Public API ────────────────────────────────────────────────────────────────

_EXERCISE_TYPE_MAP = {
    "0.1": "warm_up",
    "0.2": "range_finder",
    "0.3": "ear_training",
    "1.1": "breath_support",
    "1.2": "silent_breath",
    "1.3": "smooth_onset",
    "1.4": "legato",
    "1.5": "scale",
    "1.6": "staccato",
    "2.1": "scale_ascending",
    "2.2": "scale_descending",
    "2.3": "minor_scale",
    "2.4": "intervals",
    "2.5": "arpeggios",
    "2.6": "pitch_stability",
}


def exercise_type_from_id(exercise_id):
    for key, val in _EXERCISE_TYPE_MAP.items():
        if key in str(exercise_id):
            return val
    return "warm_up"


def analyze_audio(audio_bytes, exercise_type="warm_up"):
    """
    Analyse WAV bytes and return feedback_data dict:
    {
        "score": int,
        "xp": int,
        "feedback": [{"time": str, "message": str}, ...],
        "subscores": {dimension: int, ...},
        "duration": float,
        "pitch_data": {"f0": list, "times": list},  # for waveform overlay
    }
    """
    if not audio_bytes:
        return _short_result()

    y, sr = _load_audio(audio_bytes)
    if y is None or len(y) < int(sr * 0.4) if sr else True:
        return _short_result()

    duration = len(y) / sr

    f0, voiced_flag = _pitch_track(y, sr)
    rms              = _rms_track(y)
    n                = min(len(f0), len(voiced_flag), len(rms))
    f0, voiced_flag, rms = f0[:n], voiced_flag[:n], rms[:n]
    times            = _frames_to_time(n, sr)

    sub   = _subscores(y, sr, f0, voiced_flag, rms, exercise_type)
    score = _weighted_score(sub, exercise_type)
    xp    = _xp(score)
    fb    = _generate_feedback(y, sr, f0, voiced_flag, rms, times, exercise_type, duration)

    # Compact pitch data for waveform overlay (max 500 points)
    step = max(1, n // 500)
    pitch_data = {
        "f0":    [float(v) if not np.isnan(v) else None for v in f0[::step]],
        "times": [float(t) for t in times[::step]],
    }

    return {
        "score":      score,
        "xp":         xp,
        "feedback":   fb,
        "subscores":  sub,
        "duration":   duration,
        "pitch_data": pitch_data,
    }


def _short_result():
    return {
        "score":     0,
        "xp":        0,
        "feedback":  [{"time": "", "message": "Recording too short — hold the note for at least 1–2 seconds."}],
        "subscores": {},
        "duration":  0.0,
        "pitch_data": {"f0": [], "times": []},
    }
