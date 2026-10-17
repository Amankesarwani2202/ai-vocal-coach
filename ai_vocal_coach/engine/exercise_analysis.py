"""Exercise-aware acoustic analysis.

Pitch targets and rhythms come from the playback curriculum. Scores describe
measured audio, never an inferred physical posture or vocal register mechanism.
All event times are relative to the first performance onset.
"""

from dataclasses import dataclass
import io

import librosa
import numpy as np
import soundfile as sf
from scipy.ndimage import median_filter, uniform_filter1d
from scipy.optimize import linear_sum_assignment
from scipy.signal import find_peaks, lfilter

from utils.exercise_models import beat_grid, expected_seconds, get_profile, note_grid, target_at_times

SR = 16000
HOP = 160
FRAME = 1024


def runs(mask):
    edges = np.diff(np.r_[False, np.asarray(mask, dtype=bool), False].astype(int))
    return list(zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)))


def cents(a, b):
    return 1200 * np.log2(np.maximum(a, 1e-9) / np.maximum(b, 1e-9))


def bounded_score(value):
    return int(np.clip(round(float(value)), 0, 100))


def accuracy(error):
    return bounded_score(np.interp(error, [0, 15, 30, 50, 100, 200], [100, 90, 75, 55, 20, 0]))


@dataclass
class Features:
    y: np.ndarray
    times: np.ndarray
    rms: np.ndarray
    short_rms: np.ndarray
    f0: np.ndarray
    voiced: np.ndarray
    active: np.ndarray
    centroid: np.ndarray
    flatness: np.ndarray
    origin: float
    end: float

    @property
    def relative_times(self):
        return self.times - self.origin

    @property
    def duration(self):
        return max(0.0, self.end - self.origin)


def extract_features(audio_bytes):
    y, sr = sf.read(io.BytesIO(audio_bytes), dtype="float32", always_2d=True)
    y = np.nan_to_num(y.mean(axis=1))
    if not len(y) or sr <= 0:
        raise ValueError("No usable audio")
    if sr != SR:
        y = librosa.resample(y, orig_sr=sr, target_sr=SR)
    y = np.clip(y - np.mean(y), -1, 1)
    frames = librosa.util.frame(np.pad(y, FRAME // 2), frame_length=FRAME, hop_length=HOP).T
    rms = np.sqrt(np.mean(frames ** 2, axis=1))
    short_frames = librosa.util.frame(np.pad(y, 128), frame_length=256, hop_length=HOP).T
    short_rms = np.sqrt(np.mean(short_frames ** 2, axis=1))[:len(rms)]
    spectrum = np.abs(np.fft.rfft(frames * np.hanning(FRAME), axis=1)) + 1e-12
    frequencies = np.fft.rfftfreq(FRAME, 1 / SR)
    centroid = (spectrum * frequencies).sum(axis=1) / spectrum.sum(axis=1)
    flatness = np.exp(np.mean(np.log(spectrum), axis=1)) / np.mean(spectrum, axis=1)
    f0 = librosa.yin(y, fmin=65, fmax=1050, sr=SR, frame_length=FRAME, hop_length=HOP)
    n = min(len(f0), len(rms))
    frames, rms, spectrum, centroid, flatness, f0 = frames[:n], rms[:n], spectrum[:n], centroid[:n], flatness[:n], f0[:n]
    # Periodicity rejects noise without treating a correctly quiet hum as silence.
    periodicity = np.zeros(n)
    for i, hz in enumerate(f0):
        lag = int(round(SR / hz)) if np.isfinite(hz) and hz > 0 else 0
        if 0 < lag < FRAME // 2:
            a, b = frames[i, :-lag], frames[i, lag:]
            periodicity[i] = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12)
    gate = max(2e-5, float(np.max(rms)) * .004)
    voiced = (periodicity > .55) & (flatness < .35) & (rms > gate)
    for start, end in runs(voiced):
        if end - start < 3:
            voiced[start:end] = False
    f0 = np.where(voiced, f0, np.nan)
    active = rms > gate
    times = np.arange(n) * HOP / SR
    indices = np.flatnonzero(voiced)
    if not len(indices):
        indices = np.flatnonzero(active)
    origin = float(times[indices[0]]) if len(indices) else 0.0
    end = min(len(y) / SR, float(times[indices[-1]] + HOP / SR)) if len(indices) else 0.0
    return Features(y, times, rms, short_rms[:n], f0, voiced, active, centroid, flatness, origin, end)


def formant_track(features):
    """LPC F1/F2 with pole bandwidth and range checks, sampled every 50 ms."""
    y = librosa.resample(features.y, orig_sr=SR, target_sr=8000)
    y = lfilter([1, -.97], [1], y)
    result = np.full((len(features.times), 2), np.nan)
    for i in range(0, len(features.times), 5):
        if not features.voiced[i]:
            continue
        centre = int(features.times[i] * 8000)
        segment = y[max(0, centre - 200):centre + 200]
        if len(segment) < 320 or np.max(np.abs(segment)) < 1e-6:
            continue
        magnitude = np.abs(np.fft.rfft(segment * np.hamming(len(segment))))
        peaks, _ = find_peaks(magnitude, height=np.max(magnitude) * .035, distance=3)
        # A lone sine wave has no reliable vowel envelope, even if LPC fits poles.
        if len(peaks) < 4:
            continue
        try:
            coefficients = librosa.lpc(segment * np.hamming(len(segment)), order=14)
            poles = np.roots(coefficients)
            poles = poles[np.imag(poles) > 0]
            freq = np.angle(poles) * 8000 / (2 * np.pi)
            bandwidth = -np.log(np.maximum(np.abs(poles), 1e-8)) * 8000 / np.pi
            candidates = np.sort(freq[(bandwidth > 0) & (bandwidth < 400) & (freq > 180) & (freq < 3500)])
            if len(candidates) >= 2 and candidates[0] < 1200 and candidates[1] > 650:
                result[i:min(i + 5, len(result))] = candidates[:2]
        except (ValueError, FloatingPointError, np.linalg.LinAlgError):
            continue
    return result


def detect_attacks(features, minimum_interval=.15):
    """Combine voiced entrances with energy attacks; preserve the first note."""
    envelope = uniform_filter1d(features.rms, 3)
    rise = np.maximum(0, envelope - np.r_[envelope[0], envelope[:-1]])
    peaks, _ = find_peaks(rise, distance=max(3, int(minimum_interval * SR / HOP)), prominence=max(1e-5, np.max(rise) * .08))
    voiced_starts = [start for start, end in runs(features.voiced) if (end - start) * HOP / SR >= .08]
    candidates = sorted(set(peaks.tolist() + voiced_starts))
    candidates = [i for i in candidates if np.any(features.voiced[max(0, i - 3):i + 10])]
    selected = []
    for i in candidates:
        if not selected or features.times[i] - features.times[selected[-1]] >= minimum_interval:
            selected.append(i)
        elif rise[i] > rise[selected[-1]]:
            selected[-1] = i
    if np.any(features.voiced):
        first = int(np.flatnonzero(features.voiced)[0])
        if not selected or features.times[selected[0]] - features.times[first] > minimum_interval:
            selected.insert(0, first)
    return np.asarray(selected, dtype=int)


def internal_gaps(features, minimum=.05):
    # No fixed microphone-volume floor; a confidently tracked soft note is voiced.
    peak = np.max(features.short_rms)
    low = features.short_rms < max(1e-6, peak * .015)
    candidate = low & (~features.voiced | (features.short_rms < peak*.001))
    voiced = np.flatnonzero(features.voiced)
    if not len(voiced):
        return []
    return [(features.times[a] - features.origin, features.times[b - 1] + .01 - features.origin)
            for a, b in runs(candidate)
            if a > voiced[0]+5 and b <= voiced[-1]-5 and (b - a) * .01 >= minimum]


def match_grid(observed, expected, max_distance):
    """One-to-one matches: one attack cannot earn credit for several beats."""
    if not len(observed) or not len(expected):
        return []
    cost = np.abs(np.asarray(observed)[:, None] - np.asarray(expected)[None, :])
    rows, cols = linear_sum_assignment(cost)
    return sorted([(int(i), int(j)) for i, j in zip(rows, cols) if cost[i, j] <= max_distance])


class Report:
    def __init__(self):
        self.scores = {}
        self.feedback = []
        self.evidence = {}
        self.withheld = {}

    def event(self, code, message, time=0, metric=None, valence="negative", timing="Post-take", **evidence):
        seconds = max(0.0, float(time))
        self.feedback.append({"time": f"{int(seconds // 60)}:{seconds % 60:04.1f}", "seconds": seconds,
                              "message": message, "valence": valence, "metric": metric,
                              "rule": code, "timing": timing, "evidence": evidence,
                              **({"section": evidence["section"]} if "section" in evidence else {})})

    def metric(self, name, score, explanation, **evidence):
        score = bounded_score(score)
        self.scores[name] = score
        self.evidence[name] = evidence
        self.event("metric_" + name.lower().replace(" ", "_"), f"{name}: {score}/100. {explanation}",
                   metric=name, valence="positive" if score >= 85 else "negative" if score < 70 else "neutral", timing="Summary", **evidence)

    def unavailable(self, name, reason):
        self.withheld[name] = reason
        self.event("unavailable_" + name, reason, metric=name, valence="neutral", timing="Summary")


def _note_measurements(features, profile, context):
    bpm = context.get("bpm", profile["bpm"])
    boundaries, offsets = note_grid(profile, bpm)
    t = features.relative_times
    first = features.f0[(t >= .025) & (t < min(.35, boundaries[1] - .025)) & features.voiced]
    if not len(first):
        first = np.array([])
    root = context.get("root_hz")
    if not root:
        if not len(first):
            return [], np.full(len(t),np.nan), np.full(len(t),np.nan), None, boundaries
        # Reject a noisy/subharmonic anchor rather than silently choosing C4.
        spread = np.median(np.abs(cents(first,np.median(first))))
        if spread > 60:
            return [], np.full(len(t),np.nan), np.full(len(t),np.nan), None, boundaries
        root = float(np.median(first)) / 2 ** (offsets[0] / 12)
    target = target_at_times(profile, t, root, bpm)
    errors = cents(features.f0, target)
    measurements = []
    for i in range(len(offsets)):
        mask = (t >= boundaries[i] + .07) & (t < boundaries[i + 1] - .05) & features.voiced
        values = errors[mask]
        values = values[np.isfinite(values)]
        measurements.append({"index": i, "start": boundaries[i], "end": boundaries[i + 1], "mask": mask,
                             "error": float(np.median(values)) if len(values) else None,
                             "sd": float(np.std(values)) if len(values) else None,
                             "rms": float(np.median(features.rms[mask])) if np.any(mask) else None})
    return measurements, target, errors, root, boundaries


def _pitch_rules(features, profile, context, report):
    notes, target, errors, root, boundaries = _note_measurements(features, profile, context)
    usable = [n for n in notes if n["error"] is not None]
    comparison = np.abs(errors[np.isfinite(errors)])
    if len(comparison) and np.mean(comparison) > 1200:
        report.unavailable("Pitch Accuracy", "The generated target and performance differ by more than an octave. Target alignment is uncertain; no pitch score or sharp/flat advice is shown. Confirm your starting pitch and try again.")
        import logging
        logging.getLogger(__name__).warning("Rejected target alignment for %s: %.0f cents", profile['code'], np.mean(comparison))
        return [], np.full(len(target),np.nan), np.full(len(errors),np.nan), None
    if len(usable) < max(2, len(notes) // 2):
        report.unavailable("Pitch Accuracy", "Not enough clear notes were tracked to score this pitch pattern. Record the complete pattern again.")
        return notes, target, errors, root
    error = float(np.mean([abs(n["error"]) for n in usable]))
    report.metric("Pitch Accuracy", accuracy(error), f"The average note landing was {error:.0f} cents from the written pattern.", mean_absolute_cents=round(error, 2), notes_measured=len(usable))
    leap = profile["type"] in {"intervals", "arpeggios", "vocalises"}
    for n in usable:
        if abs(n["error"]) > 30:
            direction = "sharp" if n["error"] > 0 else "flat"
            word = "leap" if leap else "step"
            report.event("pitch_landing", f"The {word} to note {n['index'] + 1} landed {direction} — listen to that pitch and land directly on it.", n["start"], "Pitch Accuracy", deviation_cents=round(n["error"], 1))
        start = (features.relative_times >= n["start"]) & (features.relative_times < n["start"] + .22) & features.voiced
        onset_error = errors[start]
        settled = np.flatnonzero(np.abs(onset_error) < 30)
        if len(settled) and settled[0] >= 15 and onset_error[0] < -50:
            report.event("scoop", "You're sliding up into notes — try to land directly on pitch.", n["start"], "Pitch Accuracy")
    kind = profile["type"]
    if kind == "scale_ascending" and len(usable) >= 6:
        top = [n["error"] for n in notes[-3:] if n["error"] is not None]
        if len(top) >= 2 and np.mean(top) < -30 and top[-1] < top[0] - 10:
            report.event("top_flat", "The top notes went flat — take a bigger breath so you have support left for 'ti' and 'do'.", notes[-3]["start"], "Pitch Accuracy")
        baseline = np.median([n["rms"] for n in usable[:3]])
        for n in usable[-3:]:
            if 20 * np.log10(n["rms"] / (baseline + 1e-9)) > 10 and n["sd"] > 25:
                report.event("high_note_push", "You're pushing on the high notes — let airflow do the work instead of extra volume.", n["start"], "Pitch Accuracy", rms_rise_db=round(float(20*np.log10(n["rms"]/(baseline+1e-9))), 1))
    if kind == "scale_descending":
        if len(usable) > 4 and np.mean([n["error"] for n in usable[-3:]]) < -30:
            report.event("descending_flat", "Notes are sagging flat going down — keep your breath pressure up, don't ease off.", usable[-3]["start"], "Pitch Accuracy")
        if len(usable) > 1 and 20*np.log10(usable[-1]["rms"]/(usable[0]["rms"]+1e-9)) < -8:
            report.event("descending_fade", "Volume dropped near the end — maintain the same breath energy all the way down.", usable[-1]["start"], "Evenness")
        if usable[0]["sd"] > 30:
            report.event("unstable_first", "The very first note was already unstable — take a full breath before starting at the top.", 0, "Pitch Accuracy")
        if abs(usable[-1]["error"]) > max(30, 2*abs(usable[0]["error"])):
            report.event("ending_accuracy", "The ending 'do' wasn't as clean as the starting note — that's a sign of sagging support.", usable[-1]["start"], "Pitch Accuracy")
        brightness = [np.median(features.centroid[n["mask"]] / features.f0[n["mask"]]) for n in usable]
        if brightness[-1] < .65*brightness[0]:
            report.event("descending_brightness", "Your tone got duller on the way down — keep your posture and throat open, not just your breath.", usable[-1]["start"], valence="neutral", centroid_ratio=round(float(brightness[-1]/brightness[0]), 2))
    if kind == "minor_scale":
        for i in (2, 6):
            n = notes[i]
            if n["error"] is not None and 60 < n["error"] < 140:
                report.event("minor_degree", "You're pulling toward major — that note should stay natural minor, not sharpened.", n["start"], "Pitch Accuracy")
        for i in (2, 5):
            if notes[i]["error"] is not None and notes[i-1]["error"] is not None:
                interval = 100 + notes[i]["error"] - notes[i-1]["error"]
                if interval > 130:
                    report.event("wide_half_step", "That half-step is too wide — it should feel tighter than the other intervals.", notes[i]["start"], "Pitch Accuracy", interval_cents=round(interval, 1))
        if notes[0]["error"] is not None and notes[-1]["error"] is not None and abs(notes[-1]["error"]-notes[0]["error"]) > 20:
            report.event("minor_key", "You drifted from the starting pitch — keep the final octave in the same key centre.", notes[-1]["start"], "Pitch Accuracy")
    if kind == "intervals" and len(usable) == 2:
        if abs(usable[0]["error"]) <= 30 and abs(usable[1]["error"]) > 30:
            direction = "sharp" if usable[1]["error"] > 0 else "flat"
            report.event("interval_miss", f"The leap missed the target pitch — you went {direction} on the higher note.", usable[1]["start"], "Pitch Accuracy")
        if usable[1]["rms"] < .65*usable[0]["rms"]:
            report.event("second_note_weak", "Your second note was weaker than the first — keep equal energy on both pitches.", usable[1]["start"], "Evenness")
        transition = (features.relative_times >= boundaries[1]-.12) & (features.relative_times <= boundaries[1]+.12)
        if np.any(transition):
            noise = (features.flatness[transition] > .15) & (features.centroid[transition] > 2500)
            dip = np.min(features.rms[transition]) < .6*usable[0]["rms"]
            if np.any(noise) and dip:
                report.event("breath_catch", "There's a breath catch right at the leap — keep the air flowing through the jump.", boundaries[1], "Continuity")
    if kind == "arpeggios" and len(usable) >= 4:
        colours = np.array([np.median(features.centroid[n["mask"]]/features.f0[n["mask"]]) for n in usable])
        variation = float(np.std(colours)/max(np.mean(colours),1e-6))
        report.metric("Tone Colour Consistency",100-180*variation,f"Pitch-normalised spectral brightness varied by {variation:.0%} across the notes.",brightness_cv=round(variation,3))
        if variation > .25:
            report.event("arpeggio_colour", "The three notes don't match in tone — try to keep the same vocal color throughout.",metric="Tone Colour Consistency",timing="Summary")
        if np.std([n["rms"] for n in usable])/max(np.mean([n["rms"] for n in usable]),1e-6) > .25:
            report.event("arpeggio_volume", "Some notes are louder than others — even out the volume across the arpeggio.",usable[1]["start"],"Evenness")
        report.event("register_mechanism_limit", "Listen for a voice crack at the upper leap. Chest-voice weight is not inferred from brightness without a personal register baseline.",valence="neutral",timing="Summary")
    if kind in {"scale_ascending","minor_scale","vowel_ascending"} and len(usable)>=5:
        opening=np.mean([n["rms"] for n in usable[:3]])
        closing=np.mean([n["rms"] for n in usable[-3:]])
        if closing < .6*opening:
            report.event("upper_support", "Support dropped in the second half — pace your breath across the whole scale.", usable[-3]["start"],"Evenness",rms_ratio=round(closing/opening,2))
    if len(usable) >= 3:
        volumes = np.array([n["rms"] for n in usable])
        spread_db = float(np.std(20*np.log10(volumes+1e-9)))
        if not profile.get("dynamic_arc"):
            report.metric("Evenness", 100-10*spread_db, f"Note-to-note volume spread was {spread_db:.1f} dB.", rms_spread_db=round(spread_db, 2))
    # Note changes, rather than global pitch variance, provide pace measurements.
    filled = np.where(features.voiced, features.f0, np.nan)
    changes = np.abs(cents(filled[1:], filled[:-1]))
    candidates, _ = find_peaks(np.nan_to_num(changes), height=65, distance=max(8, int(.3*60/profile["bpm"]/.01)))
    if len(candidates) >= 3:
        spacing = np.diff(features.times[candidates])
        # Held final notes do not count as uneven tempo.
        cv = np.std(spacing)/max(np.mean(spacing), 1e-6)
        if cv > .2 and kind in {"scale_ascending", "scale_descending", "minor_scale"}:
            report.event("uneven_pace", "Your pace wasn't even — try to keep each note the same length.", features.relative_times[candidates[1]], "Evenness", interval_cv=round(float(cv), 2))
    return notes, target, errors, root


def _continuity_rules(features, profile, context, report):
    spb = 60/context.get("bpm", profile["bpm"])
    gaps = internal_gaps(features)
    allowed = [b*spb for b in profile.get("breath_beats", [])]
    if profile["code"]=="7.6":allowed.extend(context.get("planned_breaths",[]))
    unexpected = [(a,b) for a,b in gaps if not any(a-.15 <= point <= b+.15 for point in allowed)]
    kind = profile["type"]
    if kind == "staccato":
        boundary = 5*spb
        first = [(a,b) for a,b in gaps if b < boundary-.08]
        second = [(a,b) for a,b in unexpected if a >= boundary+.08]
        first_mean = np.mean([b-a for a,b in first]) if first else 0.0
        second_mean = np.mean([b-a for a,b in second]) if second else 0.0
        contrast = np.clip((first_mean-second_mean)/(.35*spb), 0, 1)*100
        report.metric("Contrast", contrast, f"Average separation was {first_mean:.2f}s in staccato and {second_mean:.2f}s in legato.", staccato_gap_seconds=round(float(first_mean),3),legato_gap_seconds=round(float(second_mean),3))
        if len(first) < 3:
            report.event("staccato_connected", "Part 1 is too connected — leave a clear, gentle silence between each staccato note.", 0, "Contrast", section="staccato")
        for a,b in second:
            report.event("legato_gap", "Part 2 has a break — keep the legato notes connected in one airflow.", a, "Contrast", section="legato")
        return
    connected = {"legato", "scale", "scale_ascending", "scale_descending", "minor_scale", "intervals", "arpeggios", "vowel_ascending", "vowel_modification", "legato_notes", "legato_melody", "breath_phrasing", "melodic_etude", "vocalises", "dynamic_shaping", "messa_di_voce", "mixing_registers", "portamento", "register_turning_points", "slow_melismas", "fast_runs", "pitch_stability", "capstone"}
    if kind not in connected:
        return
    gap_duration = sum(b-a for a,b in unexpected)
    report.metric("Continuity", 100-220*gap_duration/max(features.duration, .1), f"There were {len(unexpected)} unplanned breaks between confirmed sung segments, totalling {gap_duration:.2f}s.", gap_seconds=round(gap_duration, 3), gaps=len(unexpected))
    messages = {"scale_ascending": "You took an extra breath partway through — try the full scale in one breath.",
                "legato_notes": "There's a small catch between notes — try changing pitch without closing your throat.",
                "legato_melody": "There's a break between notes — keep the connection smooth like in Connecting Notes.",
                "breath_phrasing": "You breathed mid-phrase — try to hold until the end of bar 2.",
                "melodic_etude": "Your breath landed mid-phrase — the planned points are the ends of bar 4 and bar 8.",
                "vocalises": "The skips are getting re-attacked — keep the same continuous airflow across the leap as you would on a step."}
    for a,b in unexpected[:5]:
        report.event("unplanned_gap", messages.get(kind,"The phrase disconnected here — keep the airflow continuous between the notes."), a, "Continuity", gap_seconds=round(b-a,3))
    if kind == "breath_phrasing" and not unexpected:
        report.event("clean_phrase", "Nicely done — you sustained the full phrase in one breath." if not gaps else "Your breath was placed at the planned end of bar 2.", 0, "Continuity", valence="positive")


def _sustain_rules(features, profile, report):
    target = float(profile.get("min_seconds", 6))
    voiced_duration = float(np.sum(features.voiced)*.01)
    report.metric("Sustain", 100*min(voiced_duration/target,1), f"A sung signal was tracked for {voiced_duration:.1f}s against a {target:g}s target.", voiced_seconds=round(voiced_duration, 2),target_seconds=target)
    if voiced_duration < .9*target:
        report.event("short_sustain", "You ran out of air before the full hold — take a fuller breath at the start.", features.duration, "Sustain")


def _held_pitch_rules(features, profile, context, report):
    values = features.f0[features.voiced]
    if len(values) < 20:
        report.unavailable("Pitch Stability", "The sung pitch was not clear enough to measure stability. Try a quieter room and a comfortable note.")
        return
    reference = context.get("reference_hz", profile.get("reference_hz", np.median(values)))
    deviations = cents(values, reference)
    sd = float(np.std(deviations))
    trend = float(np.polyfit(features.relative_times[features.voiced], deviations, 1)[0]) if len(values)>1 else 0
    report.metric("Pitch Stability", accuracy(float(np.median(np.abs(deviations))) + .5*sd), f"Pitch variation was {sd:.0f} cents, with a drift of {trend:.1f} cents per second.", pitch_sd_cents=round(sd, 2),drift_cents_per_second=round(trend,2))
    if trend < -4:
        report.event("flat_hold", "Your pitch drifted flat as the breath ran out — keep support constant through the whole note.", features.duration/2, "Pitch Stability", timing="Real-time + Post-take")
    elif sd > 15:
        report.event("wobbly_hold", "Pitch is wobbling rather than settling — try to lock onto the note early and hold steady.", features.duration/2, "Pitch Stability", timing="Real-time + Post-take")
    if profile["type"] == "pitch_stability":
        volumes = features.rms[features.voiced]
        if np.median(volumes[-20:]) < .65*np.median(volumes[:20]):
            report.event("hold_fade", "Volume faded as you held the note — keep breath pressure even to the end.", max(0, features.duration-1), "Sustain", timing="Real-time + Post-take")
        whole = np.abs(cents(features.f0,reference))
        settled = np.flatnonzero(features.voiced & (whole <= 30))
        if len(settled) and features.relative_times[settled[0]] > .2:
            report.event("slow_settle", "You're taking too long to settle on pitch — try to land on the note right away.", features.relative_times[settled[0]], "Pitch Stability")


def _dynamic_rules(features, profile, report):
    span = (features.times >= features.origin+.08) & (features.times <= features.end-.08)
    envelope = uniform_filter1d(features.rms, 21)[span]
    if len(envelope) < 30:
        report.unavailable("Dynamic Control", "This take is too short to measure the swell and release. Record the complete soft-to-peak-to-soft arc.")
        return
    db = 20*np.log10(np.maximum(envelope,1e-6))
    # The eight-bar étude has two arcs, each peaking in the second bar of its phrase.
    if profile["type"] == "melodic_etude":
        phase = np.linspace(0,2,len(db)) % 1
    else:
        phase = np.linspace(0,1,len(db))
    desired = 1-np.abs(2*phase-1)
    spread = float(np.percentile(db,95)-np.percentile(db,5))
    correlation = float(np.corrcoef(db,desired)[0,1]) if np.std(db)>.1 else 0.0
    score = 80*max(0,correlation) + 20*np.clip(spread/3,0,1)
    if spread < .8:
        score = 15
    report.metric("Dynamic Control", score, f"The recorded volume arc varied by {spread:.1f} dB; its match to the planned swell and release was {max(0,correlation):.0%}.", range_db=round(spread,2),arc_correlation=round(correlation,3))
    if spread < 1.5 or correlation < .25:
        message = "Try shaping the phrase — a gentle swell toward the middle note, then easing back down." if profile["type"] == "legato_melody" else "Shape the phrase — a gentle rise to the peak, then ease back down."
        report.event("missing_arc", message, features.duration/2, "Dynamic Control")
    elif spread > 12 and profile["type"] in {"legato_melody","vocalises"}:
        report.event("overdone_arc", "That shape is too dramatic — make the swell more subtle.", features.duration/2, "Dynamic Control")
    elif correlation >= .7:
        report.event("smooth_arc", "The volume grew toward a controlled peak and eased back to soft smoothly.", features.duration/2, "Dynamic Control", valence="positive")


def _glide_rules(features, report):
    f0 = features.f0
    log = cents(f0,440)
    valid = features.voiced[1:] & features.voiced[:-1]
    delta = np.diff(log)[valid]
    if len(delta) < 30:
        report.unavailable("Glide Smoothness", "Not enough continuous pitch was tracked to measure this glide. Record the complete rise and return.")
        return
    speed = median_filter(delta, size=7)
    roughness = float(np.median(np.abs(delta-speed)))
    jumps = np.flatnonzero(valid & (np.nan_to_num(np.abs(np.diff(log))) > 180))
    dropouts = internal_gaps(features, .03)
    voiced = np.flatnonzero(features.voiced)
    tracking_breaks = [(features.relative_times[a],features.relative_times[b-1])
                       for a,b in runs(~features.voiced & features.active)
                       if len(voiced) and a>voiced[0]+5 and b<voiced[-1]-5 and (b-a)*.01>=.04]
    report.metric("Glide Smoothness", 100-8*roughness, f"Variation around the local glide rate was {roughness:.1f} cents per frame; intentional pitch movement is expected.", rate_roughness_cents=round(roughness,2))
    report.metric("Register Connection", 100-18*len(jumps), f"There were {len(jumps)} abrupt pitch discontinuities, {len(dropouts)} quiet interruptions, and {len(tracking_breaks)} tracking breaks during the glide.", discontinuities=len(jumps),interruptions=len(dropouts),tracking_breaks=len(tracking_breaks))
    for i in jumps[:3]:
        report.event("register_discontinuity", "There is an abrupt break in the glide here — keep the airflow and pitch moving continuously.", features.relative_times[i], "Register Connection")
    for a,b in (dropouts+tracking_breaks)[:3]:
        report.event("register_dropout", "Pitch tracking briefly dropped out during the transition — this window was excluded from connection scoring; try again a little louder or slower.", a, "Register Connection", valence="neutral")


def _vowel_rules(features, profile, context, report):
    track = formant_track(features)
    valid = np.isfinite(track).all(axis=1) & features.voiced
    coverage = np.sum(valid)/max(np.sum(features.voiced),1)
    if coverage < .3 or np.sum(valid)<20:
        report.unavailable("Vowel Consistency", "Reliable F1/F2 measurements were not available for this take. Vowel colour needs a listening check; no vowel score is shown.")
        return track
    t = features.relative_times
    # Different intended vowels are separate rounds, never inconsistency errors.
    round_seconds = profile.get("round_seconds", features.duration+.1)
    if context.get("vowel"):
        round_seconds = features.duration+.1
    groups = []
    for start in np.arange(0,max(features.duration,.1),round_seconds):
        mask = valid & (t >= start+.1) & (t < start+round_seconds-.1)
        if np.sum(mask) < 15:
            continue
        values = track[mask]
        middle = np.median(values,axis=0)
        trimmed = np.clip(values, np.percentile(values,5,axis=0), np.percentile(values,95,axis=0))
        deviation = np.std(trimmed,axis=0)/np.array([150,300])
        early = values[:max(3,len(values)//4)].mean(axis=0)
        late = values[-max(3,len(values)//4):].mean(axis=0)
        change = float(np.linalg.norm((late-early)/np.array([150,300])))
        groups.append(float(np.mean(deviation)) + .3 * change)
        if change > 1 and profile["type"] != "vowel_modification":
            message = "The vowel changed partway through — it should sound identical at the start, middle, and end."
            report.event("vowel_shift", message, start+round_seconds/2, "Vowel Consistency", timing="Real-time + Post-take", formant_change=round(change,2))
    if groups:
        report.metric("Vowel Consistency", 100-55*np.mean(groups), f"F1/F2 variation was measured within each intended vowel round ({coverage:.0%} tracking coverage).", formant_coverage=round(float(coverage),3),normalized_variation=round(float(np.mean(groups)),3))
    kind = profile["type"]
    if kind == "vowel_ascending":
        first = np.median(track[valid & (t < .5)],axis=0) if np.any(valid & (t<.5)) else None
        last = np.median(track[valid & (t > features.duration-.5)],axis=0)
        if first is not None and np.linalg.norm((last-first)/[150,300]) > 1:
            report.event("first_last_vowel", "Compare your first and last note — the top note should sound like the same vowel, just higher.", max(0,features.duration-.5), "Vowel Consistency")
    if kind == "vowel_modification":
        values=track[valid]
        shift=np.linalg.norm((np.median(values[-20:],axis=0)-np.median(values[:20],axis=0))/[150,300])
        report.event("modification_observation", f"The measured vowel-envelope change across the scale was {shift:.2f}. Listen for a small opening rather than a complete vowel change.", features.duration/2, valence="neutral")
        report.unavailable("Passaggio Timing", "An individual passaggio has not been calibrated, so modification timing and chest-voice mechanism are not scored.")
        top = features.f0[features.voiced & (t>features.duration*.6)]
        unstable = len(top)>10 and np.std(cents(top,np.median(top)))>40
        if shift<.25 and unstable:
            report.event("no_modification", "You're not modifying through the break — try letting the vowel open slightly as you approach it.",features.duration*.6,valence="neutral",formant_shift=float(shift))
        elif shift>2.5:
            report.event("large_modification", "That's too much of a shift — the vowel should still sound recognizable, just slightly opened.",features.duration*.6,valence="neutral",formant_shift=float(shift))
    vowel=context.get("vowel", profile.get("vowel"))
    # Broad vowel references are observations, not demographic-independent diagnoses.
    ranges={"A":((550,1100),(850,1800)),"E":((300,700),(1400,2600)),"I":((180,450),(1800,3400)),"O":((300,700),(650,1400)),"U":((180,450),(650,1300))}
    if vowel in ranges and np.median(features.f0[features.voiced]) < 330:
        f1,f2=np.median(track[valid],axis=0)
        limits=ranges[vowel]
        if not (limits[0][0]<=f1<=limits[0][1] and limits[1][0]<=f2<=limits[1][1]):
            report.event("vowel_reference", f"The formant profile differs from the broad '{vowel}' reference — check the mouth shape by listening before you start again.", 0, valence="neutral", f1_hz=round(float(f1)),f2_hz=round(float(f2)))
    if kind == "tongue_tension":
        report.event("tension_limit", "Tone-envelope changes can be measured, but jaw and tongue tension need your own physical check. Keep the jaw loose and the tongue released.", valence="neutral", timing="Summary")
        comfortable=context.get("comfortable_range_hz")
        if comfortable and len(comfortable)==2 and np.any(features.voiced):
            pitch=float(np.median(features.f0[features.voiced]))
            if not comfortable[0]<=pitch<=comfortable[1]:
                report.event("range_strain", "That pitch may be a stretch for you — try a more comfortable note so tension isn't coming from strain.", valence="neutral", measured_pitch_hz=round(pitch))
    return track


def _phrase_rules(features, profile, context, report):
    """Measure transition bumps and phrase endings with the written bar map."""
    boundaries,_=note_grid(profile,context.get("bpm"))
    t=features.relative_times
    allowed=np.array(profile.get("breath_beats",[]))*60/context.get("bpm",profile["bpm"])
    bumps=[]
    for point in boundaries[1:-1]:
        if len(allowed) and np.min(np.abs(allowed-point))<.1:
            continue
        transition=(t>=point-.05)&(t<point+.06)
        neighbours=((t>=point-.25)&(t<point-.08))|((t>=point+.08)&(t<point+.25))
        if not np.any(transition) or not np.any(neighbours):
            continue
        baseline=np.median(features.rms[neighbours])
        increase=20*np.log10(np.max(features.rms[transition])/(baseline+1e-9))
        if increase>4:
            bumps.append(point)
            message="There are small bumps at each note change — smooth out the breath pressure." if profile["type"]=="legato_melody" else "You're pushing extra air at each note change — keep the airflow level and let only pitch move."
            report.event("transition_bump",message,point,"Phrase Smoothness",rms_rise_db=round(float(increase),2))
    micro=internal_gaps(features,.02)
    unplanned=[(a,b) for a,b in micro if not any(a-.15<=p<=b+.15 for p in allowed)]
    report.metric("Phrase Smoothness",100-12*len(bumps)-10*len(unplanned),f"Measured {len(bumps)} volume bumps and {len(unplanned)} interruptions within the written phrases.",bumps=len(bumps),interruptions=len(unplanned))
    for a,b in unplanned:
        if b-a<.05:
            report.event("glottal_catch","There's a small catch between notes — try changing pitch without closing your throat.",a,"Phrase Smoothness",gap_seconds=round(b-a,3))
    start=features.voiced & (t>.1) & (t<min(.6,features.duration/4))
    end=features.voiced & (t>features.duration-.6)
    if np.any(start) and np.any(end):
        ratio=np.median(features.rms[end])/max(np.median(features.rms[start]),1e-9)
        if ratio<.55 and profile["type"]=="melodic_etude":
            report.event("etude_ending","The ending lost energy — the last note should sound as full as the first. You may be running low on air by bar 6.",max(0,features.duration-.6),"Phrase Smoothness",end_start_rms_ratio=round(float(ratio),2))
    if profile["type"]=="melodic_etude":
        spb=60/context.get("bpm",profile["bpm"])
        p2=features.rms[(t>=4*spb)&(t<8*spb)]
        p6=features.rms[(t>=20*spb)&(t<24*spb)]
        if len(p2) and len(p6) and np.max(p6)<1.03*np.max(p2):
            report.event("etude_climax","Bar 6 is meant to be the climax — bring a bit more intensity there than in bar 2.",20*spb,"Dynamic Control")


def _articulation_rules(features, profile, context, report):
    attacks=detect_attacks(features,.18)
    durations=[]
    for i in attacks:
        peak=min(len(features.rms)-1,i+10)
        after=features.rms[i:peak+1]
        if not len(after): continue
        top=np.max(after)
        above=np.flatnonzero(after>=.8*top)
        below=np.flatnonzero(features.rms[max(0,i-10):i+1]<=.2*top)
        begin=max(0,i-10)+(int(below[-1]) if len(below) else 0)
        finish=i+int(above[0]) if len(above) else peak
        rise=max(.01,(finish-begin)*.01)
        durations.append(rise)
        if rise>.08:
            report.event("blurry_consonant", "Your consonants are blurring into the vowel — make the attack quicker and more defined.", features.relative_times[i], "Onset Clarity", rise_ms=round(rise*1000))
    if durations:
        rise=float(np.median(durations))
        report.metric("Onset Clarity", 100-600*max(0,rise-.025), f"The median detected attack rise was {rise*1000:.0f} ms.",median_rise_ms=round(rise*1000),attacks=len(attacks))
    else:
        report.unavailable("Onset Clarity", "Clear consonant attacks were not detected. Record distinct syllables rather than one continuous vowel.")
    if profile["type"]=="consonant_clarity" and len(attacks)>=20:
        for group in range(4):
            first,last=attacks[group*5],attacks[group*5+4]
            if features.rms[last]<.65*features.rms[first]:
                syllable=['Na','Ma','La','Ra'][group]
                report.event("consonant_fade", f"The later repetitions got softer — keep the same energy on every '{syllable}'.",features.relative_times[last],"Onset Clarity")
    if profile["type"]=="diction_challenge":
        spoken=context.get("spoken_audio_bytes")
        if spoken:
            comparison=extract_features(spoken)
            spoken_attacks=detect_attacks(comparison,.15)
            def sharpness(f,idx):
                return np.median([np.max(np.diff(f.rms[max(0,i-5):i+8]))/(np.max(f.rms)+1e-9) for i in idx if i+8<len(f.rms)]) if len(idx) else np.nan
            a,b=sharpness(comparison,spoken_attacks),sharpness(features,attacks)
            if np.isfinite(a) and np.isfinite(b) and a>0:
                ratio=b/a
                report.metric("Articulation Transfer",100*min(ratio,1),f"Sung attack definition was {ratio:.0%} of the spoken baseline.",sung_to_spoken_sharpness=round(float(ratio),3))
                if ratio<.7:
                    report.event("spoken_sung_clarity","Your consonants were much clearer when spoken — bring that same crispness into the sung version.",metric="Articulation Transfer")
            else:
                report.unavailable("Articulation Transfer","The spoken and sung attacks could not be compared reliably. Record both phases clearly.")
        else:
            report.unavailable("Articulation Transfer","Record the spoken phrase first so the sung consonants can be compared with your own baseline.")
        report.event("word_endings","Listen back for word-ending consonants. Individual words are not automatically aligned, so word completion is not scored.",valence="neutral",timing="Summary")


def _resonance_rules(features, profile, report):
    t=features.relative_times
    valid=features.voiced
    brightness=features.centroid/np.maximum(features.f0,1)
    if np.sum(valid)<30:
        report.unavailable("Tone Colour Contrast","There is not enough clear sung audio to compare tone colours.")
        return
    if profile["type"]=="resonance_colours":
        values=[]
        for start in (0,3,6):
            mask=valid & (t>=start+.2) & (t<start+2.8)
            values.append(float(np.median(brightness[mask])) if np.sum(mask)>15 else np.nan)
        if np.isfinite(values).all():
            spread=(max(values)-min(values))/max(np.mean(values),1e-6)
            ordered=values[0]>values[1]>values[2]
            report.metric("Tone Colour Contrast",min(100,spread*350)*(1 if ordered else .6),f"Pitch-normalised brightness across bright, balanced, and dark rounds was {values[0]:.2f}, {values[1]:.2f}, and {values[2]:.2f}.",brightness_by_round=values)
            if spread<.12 or not ordered:
                report.event("colour_contrast","The three tone colours did not show a clear bright-to-balanced-to-dark contrast — repeat at the same comfortable pitch and change the colour gently.",metric="Tone Colour Contrast")
        else:
            report.unavailable("Tone Colour Contrast","Record all three tone-colour rounds for about three seconds each; a partial take cannot establish contrast.")
    else:
        value=float(np.median(brightness[valid]))
        report.event("brightness_observation",f"The recorded tone's pitch-normalised brightness was {value:.2f}. Compare the hum with the open vowel by listening for a forward ring.",valence="neutral",timing="Summary",spectral_brightness=value)
        report.unavailable("Resonance Placement","Forward placement and projection need a personal baseline and listening check; they are not inferred from microphone loudness.")
    report.event("resonance_limit","Spectral brightness describes this recording's colour; it does not diagnose throat tension or physical resonance placement.",valence="neutral",timing="Summary")


def _rhythm_rules(features, profile, context, report):
    spb=60/context.get("bpm",profile["bpm"])
    minimum=max(.12,spb/(profile.get("subdivisions",1)*2.5))
    clap=profile["type"]=="clap_sing"
    vocal_features=features
    if clap:
        harmonic,percussive=librosa.effects.hpss(features.y,margin=(2,5))
        buffer=io.BytesIO();sf.write(buffer,harmonic,SR,format="WAV")
        vocal_features=extract_features(buffer.getvalue())
        envelope=librosa.onset.onset_strength(y=percussive,sr=SR,hop_length=HOP)
        found=librosa.onset.onset_detect(onset_envelope=envelope,sr=SR,hop_length=HOP,units="time",backtrack=False)
        # First clap can occur at sample zero and has no preceding flux frame.
        first=np.flatnonzero(features.active)
        observed=np.unique(np.r_[features.times[first[0]] if len(first) else [],found])-features.origin
    else:
        indices=detect_attacks(features,minimum)
        observed=features.relative_times[indices]
    expected,durations=beat_grid(profile,context.get("bpm"))
    origin=context.get("performance_start_seconds")
    synchronized=origin is not None
    grid_origin=float(origin)-features.origin if synchronized else (float(observed[0]-expected[0]) if len(observed) else 0)
    grid=expected+grid_origin
    pairs=match_grid(observed,grid,spb*.6)
    if not pairs:
        report.unavailable("Beat Accuracy","Distinct attacks were not detected. Sing or clap every written attack, then record the whole pattern again.")
        return {"onsets_sec":observed.tolist(),"beat_positions":grid.tolist(),"deviations_ms":[]}
    deviations=np.array([(observed[i]-grid[j])*1000 for i,j in pairs])
    average=float(np.mean(np.abs(deviations)))
    completeness=len(pairs)/max(len(expected),len(observed),1)
    name="Off-beat Placement" if profile["type"]=="syncopation" else "Beat Accuracy"
    if profile["type"]=="syncopation" and not synchronized:
        report.unavailable(name,"Off-beat placement needs a shared click clock. Use the recorder with live cues to measure the entrance against the 'and' of 1.")
    else:
        report.metric(name,(100-average/2)*completeness,f"Matched {len(pairs)} of {len(expected)} attacks, with an average deviation of {average:.0f} ms.",average_deviation_ms=round(average,2),expected_attacks=len(expected),matched_attacks=len(pairs))
    report.metric("Pattern Completion",100*completeness,f"Detected {len(observed)} attacks for {len(expected)} written attacks.",observed_attacks=len(observed),expected_attacks=len(expected))
    if not synchronized:
        report.event("relative_clock","Timing is measured relative to your first attack. Use the recorder with live cues to also measure the first entrance against the click.",valence="neutral",timing="Summary")
    for (i,j),dev in zip(pairs,deviations):
        if abs(dev)<=60: continue
        if profile["type"]=="syncopation":
            if not synchronized: continue
            message="This note landed on the beat instead of the off-beat — delay the attack to the 'and' of 1." if abs(abs(dev)-spb*500)<60 else "The off-beat entrance isn't quite lined up — it should land exactly halfway between beats 1 and 2."
        else:
            message="You're coming in early — wait for the click before starting the note." if dev<0 else "You're landing after the click — try to anticipate the beat slightly earlier."
        report.event("beat_deviation",message,observed[i],name,deviation_ms=round(float(dev),1),expected_attack=j+1)
    if len(pairs)>=4:
        slope=float(np.polyfit([grid[j] for i,j in pairs],deviations,1)[0])
        report.metric("Tempo Consistency",100-2*abs(slope),f"Timing drift was {slope:.1f} ms per second.",drift_ms_per_second=round(slope,2))
        if abs(slope)>12:
            report.event("tempo_drift","Your timing is drifting further off as the phrase goes on — reset to the click rather than trying to catch up.",metric="Tempo Consistency",timing="Summary")
    if profile["type"]=="rhythm_compound" and len(observed)>=20:
        groups=[]
        for k in range(0,min(len(observed)-2,24),3):
            groups.extend(np.diff(observed[k:k+3]).tolist())
        if len(groups):
            cv=float(np.std(groups)/max(np.mean(groups),1e-6))
            report.metric("Compound Grouping",100-180*cv,f"Spacing variation within groups of three was {cv:.0%}.",intra_group_cv=round(cv,3))
            if cv>.2:
                report.event("compound_rushing","You're rushing the last two syllables of each beat — keep all three subdivisions evenly spaced.",metric="Compound Grouping")
        levels=[]
        for i,j in pairs:
            frame=int((observed[i]+features.origin)/.01)
            levels.append((j,float(np.max(features.rms[max(0,frame):min(len(features.rms),frame+10)]))))
        strong=[v for j,v in levels if j%3==0];weak=[v for j,v in levels if j%3]
        if strong and weak and np.mean(strong)<1.12*np.mean(weak):
            report.event("compound_stress","The strong beats (1 and 4) aren't standing out — add a bit more emphasis there to feel the compound pulse.",metric="Compound Grouping")
    # Releases are measured against energy, not just the distance to the next attack.
    measured=[]
    vf=vocal_features
    source_onsets=observed+features.origin-vf.origin
    if clap:
        source_onsets=vf.relative_times[detect_attacks(vf,spb*.6)]
        vocal_grid,vocal_durations=beat_grid(profile,context.get("bpm"),vocal=True)
        vpairs=match_grid(source_onsets+vf.origin-features.origin,vocal_grid+grid_origin,spb*.6)
        independence=len(vpairs)/max(len(vocal_grid),1)
        report.metric("Voice Independence",100*independence,f"Tracked {len(vpairs)} of {len(vocal_grid)} half-note vocal entrances independently of the claps.",vocal_entrances=len(vpairs),expected_vocal_entrances=len(vocal_grid))
        for i,j in vpairs:
            measured.append((source_onsets[i],vocal_durations[j],j))
        warm=[observed[i] for i,j in pairs if expected[j]<16*spb]
        together=[observed[i] for i,j in pairs if expected[j]>=16*spb]
        if len(warm)>3 and len(together)>3:
            before=np.std(np.diff(warm));after=np.std(np.diff(together))
            if after>max(.06,2*before):
                report.event("clap_drift","Your clapping tempo changed once you started singing — the two need to stay independent.",16*spb+grid_origin,"Voice Independence")
        if len(warm)>3 and np.std(np.diff(warm))>.06:
            report.event("clap_warmup","Get the clap pattern locked in on its own before adding the voice — your clap-only bars aren't steady yet.",0,"Beat Accuracy")
    else:
        measured=[(source_onsets[i],durations[j],j) for i,j in pairs]
    ratios=[]
    for start,desired,j in measured:
        begin=int(round((start+vf.origin)/.01))
        stop=min(len(vf.rms),int((start+vf.origin+desired+.15)/.01))
        region=vf.rms[max(0,begin):stop]
        if len(region)<5: continue
        quiet=region<max(np.max(region)*.2,1e-6)
        release=next((a for a,b in runs(quiet) if a>5 and b-a>=4),len(region))
        actual=release*.01
        ratios.append(min(actual/desired,1.2))
        if actual<.85*desired:
            message={"rhythm_quarters":"The long note is ending early — hold it for its full two beats.","syncopation":"The syncopated note is cutting off early — it should ring through until the next attack point.","clap_sing":"The sung note is ending early — let it ring for its full two beats even while you keep clapping."}.get(profile["type"],"Release each note cleanly just before the next click; do not cut it short.")
            if profile["type"]!="rhythm_quarters" or j%3==2:
                report.event("short_rhythm_note",message,start+vf.origin-features.origin,"Note Values",duration_seconds=round(actual,2),target_seconds=round(float(desired),2))
    if ratios:
        report.metric("Note Values",100-150*np.mean(np.abs(np.asarray(ratios)-1)),"Note releases were compared with the written beat lengths.",mean_duration_ratio=round(float(np.mean(ratios)),3))
    if profile["type"]=="rhythm_quarters" and np.sum(features.voiced)>20:
        sd=float(np.std(cents(features.f0[features.voiced],np.median(features.f0[features.voiced]))))
        if sd>30:
            report.event("rhythm_pitch","Pitch drifted during the pattern — this exercise is about rhythm, so keep the pitch fixed on one note.",valence="negative")
    return {"onsets_sec":observed.tolist(),"beat_positions":grid.tolist(),"deviations_ms":deviations.tolist(),"avg_deviation_ms":round(average,2),"synchronized":synchronized,"expected_durations_sec":durations.tolist()}


def invalid_result(message):
    return {"score":0,"xp":0,"subscores":{},"feedback":[{"time":"","seconds":0,"message":message,"valence":"neutral","rule":"invalid_recording","timing":"Summary"}],"duration":0,"performance_duration":0,"pitch_data":{"f0":[],"times":[]},"complete":False,"withheld_metrics":{}}


def analyze_exercise(audio_bytes, exercise, context=None):
    context=dict(context or {})
    profile=get_profile(exercise)
    if context.get("profile_overrides"):
        profile.update(context["profile_overrides"])
    if not audio_bytes:
        return invalid_result("No recording was received. Please record an attempt first.")
    try:
        f=extract_features(audio_bytes)
    except (ValueError,RuntimeError,sf.LibsndfileError):
        return invalid_result("The recording could not be read. Please record again or upload a WAV file.")
    if f.duration<.3 or np.max(f.rms)<2e-5:
        return invalid_result("No clear performance was detected. Move closer to the microphone and record again.")
    # Shared valid-performance boundary: centred YIN/RMS frames near the
    # cutoff contain padding and must not affect any score, event or chart.
    valid_end = max(f.origin, f.end - FRAME / (2 * SR))
    valid = (f.times >= f.origin) & (f.times < valid_end)
    f.voiced &= valid
    f.active &= valid
    f.f0 = np.where(f.voiced, f.f0, np.nan)
    model=profile["pitch_model"]
    if profile["type"] == "clap_sing":
        active = np.flatnonzero(f.active)
        if len(active):
            f.origin = float(f.times[active[0]])
            f.end = float(f.times[active[-1]]) + .01
    if model not in {"breath","rhythm"} and np.sum(f.voiced)<15:
        return invalid_result("A clear sung signal could not be tracked. Try a comfortable pitch in a quiet room.")
    report=Report()
    target=np.full(len(f.times),np.nan)
    errors=np.full(len(f.times),np.nan)
    root=None
    notes=None
    if model=="stepped" and profile["code"]!="7.3":
        notes,target,errors,root=_pitch_rules(f,profile,context,report)
    elif profile['code']=='7.3':
        main=f.f0[f.voiced & (f.relative_times>=.2) & (f.relative_times<.7)]
        if len(main)>=4:
            root=float(np.median(main))
            target=target_at_times(profile,f.relative_times,root,context.get('bpm'))
            errors=cents(f.f0,target)
    elif model=="held":
        _held_pitch_rules(f,profile,context,report)
    elif model=="glide":
        _glide_rules(f,report)
        if profile.get('segments'):
            start=f.f0[f.voiced & (f.relative_times>=.08) & (f.relative_times<.4)]
            if len(start):
                root=context.get('root_hz') or float(np.median(start))
                for seg in profile['segments']:
                    mask=(f.relative_times>=seg['start'])&(f.relative_times<seg['end'])
                    offset=np.interp(f.relative_times[mask],[seg['start'],seg['end']],[seg['from'],seg['to']])
                    target[mask]=root*2**(offset/12)
                # Deviation markers belong to held arrivals, not the glide path.

    if profile["code"]!="7.3":
        _continuity_rules(f,profile,context,report)
    if profile.get("dynamic_arc"):
        _dynamic_rules(f,profile,report)
    if profile["type"] in {"pitch_stability","dynamic_shaping","messa_di_voce","forward_placement","resonance_colours"}:
        _sustain_rules(f,profile,report)
    vowel_types={"vowel_sustain","vowel_ascending","vowel_modification","consonant_clarity","tongue_tension","diction_challenge"}
    if profile["type"] in vowel_types:
        _vowel_rules(f,profile,context,report)
    if profile["type"] in {"legato_notes","legato_melody","breath_phrasing","melodic_etude","vocalises"}:
        _phrase_rules(f,profile,context,report)
        _vowel_rules(f,profile,context,report)
    if profile["type"] in {"consonant_clarity","diction_challenge","smooth_onset"}:
        _articulation_rules(f,profile,context,report)
    if profile["type"] in {"forward_placement","resonance_colours"}:
        _resonance_rules(f,profile,report)
    timing_data=None
    if model=="rhythm":
        timing_data=_rhythm_rules(f,profile,context,report)
    if model=="breath":
        region=f.rms[f.active]
        spread=float(np.std(region)/max(np.mean(region),1e-9))
        report.metric("Airflow Steadiness",100-100*spread,f"Exhalation energy varied by {spread:.0%} relative to its mean.",rms_cv=round(spread,3))
        target_seconds=profile.get("min_seconds",8)
        report.metric("Support Duration",100*min(f.duration/target_seconds,1),f"The exhalation lasted {f.duration:.1f}s against a {target_seconds:g}s target.",duration_seconds=round(f.duration,2),target_seconds=target_seconds)
    if profile['code']=='7.4':
        _vowel_rules(f,profile,context,report)
    if profile['code'].startswith('7.'):
        from engine.level_seven import evaluate
        evaluate(f,profile,context,report,notes,root)
    if not report.scores and not profile['code'].startswith('7.'):
        report.metric("Voice Presence",100*np.mean(f.voiced[(f.times>=f.origin)&(f.times<=f.end)]),"This measures how consistently a sung signal was tracked, rather than a pitch or placement target.",voiced_frames=int(np.sum(f.voiced)))
    planned=expected_seconds(profile,context.get("bpm"))
    minimum=profile.get("min_seconds",planned*.85 if profile.get("notes") or profile.get("total_beats") else .8)
    complete=f.duration+.08>=minimum and bool(report.scores)
    if profile["code"]=="7.5" and root is None:
        complete=False
    if profile["type"]=="clap_sing":
        # The first clap anchors the combined take, not the later vocal entrance.
        active=np.flatnonzero(f.active)
        complete=(f.times[active[-1]]-f.times[active[0]]+.08>=minimum) if len(active) else False
    if f.duration+.08<minimum:
        report.event("ended_early",f"Recording ended early: {f.duration:.1f}s of performance was detected; this attempt needs about {minimum:.1f}s. Record all sections before saving progress.",f.duration,valence="neutral",timing="Summary",minimum_seconds=round(float(minimum),2))
    scores=report.scores
    score=bounded_score(np.mean(list(scores.values()))) if scores else 0
    # Specific events first; every scored metric keeps its evidence summary.
    specific=[item for item in report.feedback if item["timing"]!="Summary"]
    summaries=[item for item in report.feedback if item["timing"]=="Summary"]
    seen=set();events=[]
    for item in specific:
        identity=(item["rule"],int(item["seconds"]*2),item.get("metric"))
        if identity not in seen:
            events.append(item);seen.add(identity)
    span=(f.times>=f.origin)&(f.times<valid_end)
    selected=np.flatnonzero(span)[::max(1,int(np.sum(span)//1000))]
    plot={"times":f.relative_times[selected].tolist(),"f0":[float(v) if np.isfinite(v) else None for v in f.f0[selected]],"target_f0":[float(v) if np.isfinite(v) else None for v in target[selected]],"deviation_cents":[float(v) if np.isfinite(v) else None for v in errors[selected]],"root_hz":root}
    result={"score":score,"xp":max(10,int(score*.6)) if complete else 0,"subscores":scores,"feedback":events[:12]+summaries,"duration":len(f.y)/SR,"performance_duration":f.duration,"pitch_data":plot,"complete":bool(complete),"metric_evidence":report.evidence,"withheld_metrics":report.withheld,"profile":profile,"analysis_meta":{"engine":"exercise-aware YIN + LPC","sample_rate":SR,"onset_offset_seconds":f.origin,"valid_performance_end_seconds":valid_end-f.origin,"scoring_version":"level7-v2","pitch_model":model,"relative_target":not bool(context.get("root_hz")),"bpm":context.get("bpm",profile["bpm"])}}
    if profile["code"]=="7.6":
        result["reflection_only"]=True
        result["xp"]=0
    if timing_data is not None:
        result["timing_data"]=timing_data
    return result
