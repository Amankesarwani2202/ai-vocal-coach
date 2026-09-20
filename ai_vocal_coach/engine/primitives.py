"""
Shared analysis primitives for error detection.

All functions operate on numpy arrays and return numpy arrays or scalars.
No Streamlit dependency — pure signal processing.
"""

import numpy as np

try:
    import librosa
    import librosa.feature
    import librosa.onset
    LIBROSA_OK = True
except ImportError:
    librosa = None
    LIBROSA_OK = False

HOP = 512
FRAME = 2048
MIN_F0 = 65.0
MAX_F0 = 1050.0

# ── Pitch in cents ────────────────────────────────────────────────────────

def hz_to_midi(hz):
    """Convert Hz array to MIDI note numbers. Non-positive values become NaN."""
    hz = np.asarray(hz, dtype=float)
    out = np.full_like(hz, np.nan)
    pos = hz > 0
    out[pos] = 69.0 + 12.0 * np.log2(hz[pos] / 440.0)
    return out


def pitch_deviation_cents(f0, expected_midi, sr=22050):
    """
    Per-frame signed deviation in cents from the expected MIDI note.

    Parameters
    ----------
    f0 : array  — detected pitch in Hz (0 or NaN = unvoiced)
    expected_midi : float or array  — target MIDI note(s)
    sr : int  — sample rate (unused, kept for API consistency)

    Returns
    -------
    cents : array  — signed deviation; NaN where f0 is unvoiced
    """
    f0 = np.asarray(f0, dtype=float)
    expected_midi = np.asarray(expected_midi, dtype=float)
    expected_hz = 440.0 * (2.0 ** ((expected_midi - 69.0) / 12.0))
    cents = np.full_like(f0, np.nan)
    valid = np.isfinite(f0) & (f0 > 0)
    if np.any(valid):
        if expected_hz.ndim == 0:
            ref = float(expected_hz)
        else:
            ref = np.broadcast_to(expected_hz, f0.shape)[valid]
        cents[valid] = 1200.0 * np.log2(f0[valid] / ref)
    return cents


def pitch_segments_cents(f0, times, pattern_semitones, anchor_hz=None):
    """
    For a scale/arpeggio exercise, compute per-note deviation in cents.

    Splits the recording into equal-duration segments (one per note in
    the pattern) and returns the median deviation in each segment.

    Returns
    -------
    list of dicts: [{note_index, time_s, median_cents, std_cents, expected_midi}, ...]
    """
    f0 = np.asarray(f0, dtype=float)
    times = np.asarray(times, dtype=float)
    pattern = np.asarray(pattern_semitones, dtype=float)

    valid = np.isfinite(f0) & (f0 > 0)
    if np.sum(valid) < 4 or len(times) == 0:
        return []

    if anchor_hz is None:
        anchor_hz = float(np.median(f0[valid][:max(3, np.sum(valid) // 8)]))
    if anchor_hz <= 0:
        return []

    anchor_midi = 69.0 + 12.0 * np.log2(anchor_hz / 440.0)
    duration = float(times[-1]) if len(times) > 0 else 1.0
    n_notes = len(pattern)
    note_dur = duration / n_notes

    results = []
    for i, semi in enumerate(pattern):
        t_start = i * note_dur
        t_end = (i + 1) * note_dur
        mask = valid & (times >= t_start) & (times < t_end)
        expected_midi = anchor_midi + semi
        expected_hz = 440.0 * (2.0 ** ((expected_midi - 69.0) / 12.0))
        seg_f0 = f0[mask]
        if len(seg_f0) < 2:
            results.append({
                "note_index": i, "time_s": (t_start + t_end) / 2,
                "median_cents": np.nan, "std_cents": np.nan,
                "expected_midi": expected_midi,
            })
            continue
        cents = 1200.0 * np.log2(seg_f0 / expected_hz)
        results.append({
            "note_index": i,
            "time_s": (t_start + t_end) / 2,
            "median_cents": float(np.nanmedian(cents)),
            "std_cents": float(np.nanstd(cents)),
            "expected_midi": expected_midi,
        })
    return results


# ── RMS envelope ──────────────────────────────────────────────────────────

def rms_short(y, sr=22050, window_ms=50):
    """Short-window RMS for note-level checks."""
    frame_len = max(64, int(sr * window_ms / 1000))
    hop = frame_len // 2
    n = max(1, int(np.ceil(len(y) / hop)))
    out = np.zeros(n, dtype=np.float64)
    for i in range(n):
        s = i * hop
        e = min(s + frame_len, len(y))
        seg = y[s:e]
        if len(seg):
            out[i] = float(np.sqrt(np.mean(seg ** 2)))
    return out, hop


def rms_long(y, sr=22050, window_ms=500):
    """Long-window RMS for phrase-level trends (fades, swells, arcs)."""
    return rms_short(y, sr, window_ms)


def rms_db(rms_linear):
    """Convert linear RMS to dB (relative to max)."""
    rms_linear = np.asarray(rms_linear, dtype=float)
    ref = np.max(rms_linear)
    if ref < 1e-10:
        return np.full_like(rms_linear, -60.0)
    return 20.0 * np.log10(np.clip(rms_linear, 1e-10, None) / ref)


def rms_per_note(rms, times, n_notes, duration):
    """Average RMS per note segment."""
    rms = np.asarray(rms, dtype=float)
    times = np.asarray(times, dtype=float)
    note_dur = duration / n_notes
    result = []
    for i in range(n_notes):
        t0 = i * note_dur
        t1 = (i + 1) * note_dur
        mask = (times >= t0) & (times < t1) & np.isfinite(rms)
        seg = rms[mask]
        result.append(float(np.mean(seg)) if len(seg) > 0 else 0.0)
    return result


# ── Onset / offset detection ─────────────────────────────────────────────

def detect_onsets(y, sr=22050):
    """
    Detect note onsets. Returns onset times in seconds and frame indices.
    Uses librosa spectral flux with amplitude derivative fallback.
    """
    if LIBROSA_OK:
        try:
            frames = librosa.onset.onset_detect(
                y=y, sr=sr, hop_length=HOP, backtrack=False)
            times = librosa.frames_to_time(frames, sr=sr, hop_length=HOP)
            return times, frames
        except Exception:
            pass
    # Amplitude-derivative fallback
    rms, hop = rms_short(y, sr, 50)
    if len(rms) < 3:
        return np.array([]), np.array([], dtype=int)
    diff = np.diff(rms)
    threshold = np.std(diff) * 1.5
    peaks = np.where(diff > threshold)[0] + 1
    # Remove onsets too close together
    if len(peaks) > 1:
        keep = [peaks[0]]
        for p in peaks[1:]:
            if (p - keep[-1]) * hop / sr > 0.08:
                keep.append(p)
        peaks = np.array(keep)
    times = peaks.astype(float) * hop / sr
    return times, peaks


def onset_sharpness(y, sr, onset_times):
    """
    Measure how sharp each onset is (rise time in ms).
    Returns list of (onset_time_s, rise_time_ms).
    """
    rms, hop = rms_short(y, sr, 30)
    results = []
    for t in onset_times:
        frame = int(t * sr / hop)
        if frame >= len(rms) or frame < 2:
            continue
        # Look back up to 10 frames for the start of the rise
        start = max(0, frame - 10)
        segment = rms[start:frame + 1]
        if len(segment) < 2:
            continue
        peak_val = float(np.max(segment))
        if peak_val < 1e-8:
            continue
        threshold = peak_val * 0.2
        rise_frames = 0
        for j in range(len(segment) - 1, -1, -1):
            if segment[j] < threshold:
                rise_frames = len(segment) - 1 - j
                break
        rise_ms = rise_frames * hop / sr * 1000
        results.append((float(t), float(rise_ms)))
    return results


def note_durations(onset_times, total_duration):
    """Compute duration of each note from onset timestamps."""
    if len(onset_times) < 1:
        return []
    onset_times = np.asarray(onset_times, dtype=float)
    ends = np.append(onset_times[1:], total_duration)
    return list(ends - onset_times)


# ── Silence / gap detection ──────────────────────────────────────────────

def detect_gaps(rms, voiced_flag, sr, min_gap_s=0.20):
    """
    Detect silence gaps in the recording.

    Returns list of (start_s, end_s, duration_s).
    """
    rms = np.asarray(rms, dtype=float)
    voiced = np.asarray(voiced_flag, dtype=bool)
    n = min(len(rms), len(voiced))
    if n == 0:
        return []

    voiced_rms = rms[:n][voiced[:n] & np.isfinite(rms[:n]) & (rms[:n] > 1e-7)]
    if len(voiced_rms) < 3:
        return []
    typical = float(np.median(voiced_rms))
    if typical < 1e-8:
        return []
    silence_thresh = max(typical * 0.13, 1e-4)

    low = (rms[:n] < silence_thresh) & ~voiced[:n]
    frames_required = max(2, int(min_gap_s * sr / HOP))

    gaps = []
    i = 0
    while i < n:
        if not low[i]:
            i += 1
            continue
        start = i
        while i < n and low[i]:
            i += 1
        if i - start >= frames_required:
            t_start = start * HOP / sr
            t_end = i * HOP / sr
            gaps.append((float(t_start), float(t_end), float(t_end - t_start)))
    return gaps


def has_audible_gasp(y, sr, first_onset_s):
    """
    Check for high-frequency noise burst before the first onset.
    Returns True if an audible gasp is detected.
    """
    if first_onset_s is None or first_onset_s < 0.05:
        return False
    end_sample = int(first_onset_s * sr)
    if end_sample < 256:
        return False
    pre = y[:end_sample]
    rms_val = float(np.sqrt(np.mean(pre ** 2)))
    if rms_val < 1e-5:
        return False
    # Check spectral centroid — gasps have high-frequency content without pitch
    win = min(len(pre), FRAME)
    mag = np.abs(np.fft.rfft(pre[-win:] * np.hanning(win)))
    freqs = np.fft.rfftfreq(win, d=1.0 / sr)
    total = float(np.sum(mag))
    if total < 1e-10:
        return False
    centroid = float(np.dot(freqs, mag) / total)
    return centroid > 2000 and rms_val > 1e-4


# ── LPC-based formant tracking ───────────────────────────────────────────

def lpc_formants(y, sr, n_formants=3, frame_len=None, hop_len=None):
    """
    LPC-based F1/F2 formant estimation per frame.

    Returns array of shape (n_frames, n_formants) with formant frequencies in Hz.
    NaN where formants cannot be estimated.
    """
    if frame_len is None:
        frame_len = int(sr * 0.025)  # 25 ms
    if hop_len is None:
        hop_len = int(sr * 0.010)  # 10 ms

    lpc_order = 2 + int(sr / 1000)
    n_frames = max(1, int(np.ceil((len(y) - frame_len) / hop_len)) + 1)
    formants = np.full((n_frames, n_formants), np.nan)

    for i in range(n_frames):
        start = i * hop_len
        end = start + frame_len
        if end > len(y):
            break
        frame = y[start:end].copy()
        # Pre-emphasis
        frame = np.append(frame[0], frame[1:] - 0.97 * frame[:-1])
        frame *= np.hamming(len(frame))

        rms_val = float(np.sqrt(np.mean(frame ** 2)))
        if rms_val < 1e-6:
            continue

        try:
            # Levinson-Durbin via numpy
            r = np.correlate(frame, frame, mode='full')
            r = r[len(frame) - 1:]
            r = r[:lpc_order + 1]
            if r[0] < 1e-10:
                continue
            # Solve using Toeplitz
            from numpy.linalg import solve
            R = np.zeros((lpc_order, lpc_order))
            for row in range(lpc_order):
                for col in range(lpc_order):
                    R[row, col] = r[abs(row - col)]
            a = solve(R, r[1:lpc_order + 1])
            coeffs = np.concatenate(([1.0], -a))

            roots = np.roots(coeffs)
            roots = roots[np.imag(roots) >= 0]
            angles = np.arctan2(np.imag(roots), np.real(roots))
            freqs_hz = angles * sr / (2.0 * np.pi)
            # Keep only valid formant frequencies
            valid = (freqs_hz > 90) & (freqs_hz < sr / 2 - 50)
            freqs_hz = np.sort(freqs_hz[valid])

            for j in range(min(n_formants, len(freqs_hz))):
                formants[i, j] = freqs_hz[j]
        except Exception:
            continue

    return formants


def formant_track_f1_f2(y, sr):
    """Convenience: return (f1_track, f2_track) arrays."""
    fmt = lpc_formants(y, sr, n_formants=2)
    return fmt[:, 0], fmt[:, 1]


# ── Spectral centroid and tilt ────────────────────────────────────────────

def spectral_centroid_track(y, sr):
    """Per-frame spectral centroid in Hz."""
    if LIBROSA_OK:
        try:
            sc = librosa.feature.spectral_centroid(
                y=y, sr=sr, hop_length=HOP, n_fft=FRAME)[0]
            return np.asarray(sc, dtype=np.float64)
        except Exception:
            pass
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)
    freqs = np.fft.rfftfreq(FRAME, d=1.0 / sr)
    win = np.hanning(FRAME)
    for i in range(n):
        s, e = i * HOP, min(i * HOP + FRAME, len(y))
        frame = y[s:e]
        if len(frame) < FRAME:
            frame = np.pad(frame, (0, FRAME - len(frame)))
        mag = np.abs(np.fft.rfft(frame * win))
        total = float(np.sum(mag))
        if total > 1e-10:
            out[i] = float(np.dot(freqs, mag) / total)
    return out


def spectral_tilt(y, sr):
    """
    Per-frame spectral tilt (slope of log-magnitude spectrum in dB/octave).
    Negative = more energy in lower frequencies (normal voice).
    Approximation: ratio of energy below 2kHz vs above 2kHz.
    """
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)
    freqs = np.fft.rfftfreq(FRAME, d=1.0 / sr)
    win = np.hanning(FRAME)
    split_bin = np.searchsorted(freqs, 2000)

    for i in range(n):
        s, e = i * HOP, min(i * HOP + FRAME, len(y))
        frame = y[s:e]
        if len(frame) < FRAME:
            frame = np.pad(frame, (0, FRAME - len(frame)))
        mag = np.abs(np.fft.rfft(frame * win)) ** 2
        low = float(np.sum(mag[:split_bin]))
        high = float(np.sum(mag[split_bin:]))
        if low > 1e-10 and high > 1e-10:
            out[i] = 10.0 * np.log10(low / high)
        else:
            out[i] = 0.0
    return out


# ── Scooping detector ────────────────────────────────────────────────────

def detect_scoops(f0, times, onset_times, threshold_ms=150):
    """
    Detect scooping into notes (pitch sliding up to target over > threshold_ms).
    Returns list of (onset_time_s, scoop_duration_ms).
    """
    f0 = np.asarray(f0, dtype=float)
    times = np.asarray(times, dtype=float)
    results = []
    for onset_t in onset_times:
        idx = np.searchsorted(times, onset_t)
        if idx >= len(f0) - 5:
            continue
        # Look at the next ~500ms after onset
        window_end = np.searchsorted(times, onset_t + 0.5)
        seg = f0[idx:window_end]
        valid = np.isfinite(seg) & (seg > 0)
        if np.sum(valid) < 3:
            continue
        seg_valid = seg[valid]
        target = float(np.median(seg_valid[-max(2, len(seg_valid) // 3):]))
        if target <= 0:
            continue
        cents_from_target = np.abs(1200.0 * np.log2(seg_valid / target))
        # Find first frame within 15 cents of target
        settled = np.where(cents_from_target < 15)[0]
        if len(settled) == 0:
            continue
        settle_frame = settled[0]
        settle_time_ms = settle_frame * (times[1] - times[0]) * 1000 if len(times) > 1 else 0
        if settle_time_ms > threshold_ms:
            results.append((float(onset_t), float(settle_time_ms)))
    return results


# ── Chest-voice weight proxy ─────────────────────────────────────────────

def chest_voice_weight(y, sr, times=None):
    """
    Heuristic proxy for chest-voice registration.

    Approximation: measures the ratio of energy below ~800 Hz to total energy.
    Higher values suggest heavier chest mechanism. This is a rough spectral
    proxy, not a physiological measurement.
    """
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)
    freqs = np.fft.rfftfreq(FRAME, d=1.0 / sr)
    win = np.hanning(FRAME)
    split_bin = np.searchsorted(freqs, 800)

    for i in range(n):
        s, e = i * HOP, min(i * HOP + FRAME, len(y))
        frame = y[s:e]
        if len(frame) < FRAME:
            frame = np.pad(frame, (0, FRAME - len(frame)))
        mag = np.abs(np.fft.rfft(frame * win)) ** 2
        total = float(np.sum(mag))
        if total > 1e-10:
            out[i] = float(np.sum(mag[:split_bin])) / total
    return out


# ── Pharyngeal constriction proxy ─────────────────────────────────────────

def pharyngeal_constriction(y, sr):
    """
    Heuristic proxy for pharyngeal constriction / throaty tone.

    Approximation: looks for elevated energy in the 800-2000 Hz range
    with reduced energy above 3000 Hz, suggesting a constricted throat.
    This is a rough spectral proxy, not a physiological measurement.
    """
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)
    freqs = np.fft.rfftfreq(FRAME, d=1.0 / sr)
    win = np.hanning(FRAME)
    low_bin = np.searchsorted(freqs, 800)
    mid_bin = np.searchsorted(freqs, 2000)
    high_bin = np.searchsorted(freqs, 3000)

    for i in range(n):
        s, e = i * HOP, min(i * HOP + FRAME, len(y))
        frame = y[s:e]
        if len(frame) < FRAME:
            frame = np.pad(frame, (0, FRAME - len(frame)))
        mag = np.abs(np.fft.rfft(frame * win)) ** 2
        mid_energy = float(np.sum(mag[low_bin:mid_bin]))
        high_energy = float(np.sum(mag[high_bin:]))
        if mid_energy > 1e-10 and high_energy > 1e-10:
            out[i] = mid_energy / (high_energy + 1e-10)
        elif mid_energy > 1e-10:
            out[i] = 10.0  # Very constricted
    return out
