"""
Robust vocal audio analysis engine.

Primary goals:
    1. Stable pitch tracking using librosa.pyin
    2. Removal of octave jumps and pitch outliers
    3. Better distinction between real silence and pYIN uncertainty
    4. More stable vocal-energy scoring
    5. More conservative and useful coaching feedback
    6. Backward-compatible output for exercise_flow.py

The public API remains:

    exercise_type_from_id(exercise_id)
    analyze_audio(audio_bytes, exercise_type="warm_up")

analyze_audio() returns:

{
    "score": int,
    "xp": int,
    "feedback": [{"time": str, "message": str}],
    "subscores": {...},
    "duration": float,
    "pitch_data": {
        "f0": [...],
        "times": [...]
    }
}
"""

import io
import wave as _wave

import numpy as np


# ---------------------------------------------------------------------------
# Optional librosa import
# ---------------------------------------------------------------------------

try:
    import librosa
    import librosa.feature
    import librosa.onset

    LIBROSA_OK = True
    LIBROSA_VERSION = getattr(librosa, "__version__", "unknown")
except ImportError:
    librosa = None
    LIBROSA_OK = False
    LIBROSA_VERSION = None


# ---------------------------------------------------------------------------
# Analysis configuration
# ---------------------------------------------------------------------------

HOP = 512
FRAME = 2048

MIN_RECORDING_SECONDS = 0.8

MIN_F0 = 65.0
MAX_F0 = 1050.0

# Pitch confidence / quality
MIN_VOICED_FRAMES = 6

# A real gap should normally last at least this long.
MIN_GAP_SECONDS = 0.30

# Ignore very small variations in the first/last part of a recording.
EDGE_IGNORE_SECONDS = 0.20

# Number of feedback messages returned to the UI.
MAX_FEEDBACK_ITEMS = 8


# ---------------------------------------------------------------------------
# Audio loading
# ---------------------------------------------------------------------------

def _load_audio(audio_bytes):
    """
    Load WAV/audio bytes into mono float32 audio.

    Returns:
        (y, sr)

    or:
        (None, None)
    """

    if not audio_bytes:
        return None, None

    # Primary path: librosa
    if LIBROSA_OK:
        try:
            y, sr = librosa.load(
                io.BytesIO(audio_bytes),
                sr=None,
                mono=True,
            )

            y = np.asarray(y, dtype=np.float32)

            if len(y) == 0:
                return None, None

            # Remove NaN/Inf values defensively.
            y = np.nan_to_num(
                y,
                nan=0.0,
                posinf=0.0,
                neginf=0.0,
            )

            return y, int(sr)

        except Exception:
            pass

    # Fallback WAV parser
    try:
        with _wave.open(io.BytesIO(audio_bytes), "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            sr = wf.getframerate()
            frames = wf.readframes(wf.getnframes())

        if not frames:
            return None, None

        # 16-bit WAV is what st.audio_input normally provides.
        if sample_width == 2:
            raw = np.frombuffer(
                frames,
                dtype=np.int16,
            ).astype(np.float32)

            scale = 32768.0

        elif sample_width == 1:
            raw = np.frombuffer(
                frames,
                dtype=np.uint8,
            ).astype(np.float32)

            raw = raw - 128.0
            scale = 128.0

        elif sample_width == 4:
            raw = np.frombuffer(
                frames,
                dtype=np.int32,
            ).astype(np.float32)

            scale = 2147483648.0

        else:
            return None, None

        if channels > 1:
            raw = raw.reshape(-1, channels).mean(axis=1)

        y = raw / scale
        y = np.nan_to_num(
            y,
            nan=0.0,
            posinf=0.0,
            neginf=0.0,
        )

        return y.astype(np.float32), int(sr)

    except Exception:
        return None, None


# ---------------------------------------------------------------------------
# Basic signal helpers
# ---------------------------------------------------------------------------

def _rms_track(y):
    """
    RMS energy at HOP intervals.
    """

    if y is None or len(y) == 0:
        return np.array([], dtype=np.float64)

    if LIBROSA_OK:
        try:
            rms = librosa.feature.rms(
                y=y,
                frame_length=FRAME,
                hop_length=HOP,
            )[0]

            return np.asarray(rms, dtype=np.float64)

        except Exception:
            pass

    # Numpy fallback
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)

    for i in range(n):
        start = i * HOP
        end = min(start + FRAME, len(y))
        segment = y[start:end]

        if len(segment):
            out[i] = float(
                np.sqrt(np.mean(np.square(segment)))
            )

    return out


def _frames_to_time(n, sr):
    """
    Convert frame indexes to seconds.
    """

    if n <= 0 or sr <= 0:
        return np.array([], dtype=np.float64)

    if LIBROSA_OK:
        try:
            return librosa.frames_to_time(
                np.arange(n),
                sr=sr,
                hop_length=HOP,
            )
        except Exception:
            pass

    return np.arange(n, dtype=np.float64) * HOP / float(sr)


def _safe_percentile(values, percentile, default=0.0):
    values = np.asarray(values, dtype=float)

    values = values[np.isfinite(values)]

    if len(values) == 0:
        return float(default)

    return float(np.percentile(values, percentile))


def _median_filter_1d(values, radius=2):
    """
    Small dependency-free median filter.
    NaNs are ignored where possible.
    """

    values = np.asarray(values, dtype=float)

    if len(values) < 3:
        return values.copy()

    result = values.copy()

    for i in range(len(values)):
        start = max(0, i - radius)
        end = min(len(values), i + radius + 1)

        window = values[start:end]
        finite = window[np.isfinite(window)]

        if len(finite):
            result[i] = float(np.median(finite))

    return result


# ---------------------------------------------------------------------------
# Energy / activity detection
# ---------------------------------------------------------------------------

def _energy_gate(rms):
    """
    Estimate an adaptive vocal activity threshold.

    We deliberately do NOT use a fixed amplitude threshold because
    microphone levels vary significantly between laptops/phones/browsers.

    Returns:
        threshold, active_mask
    """

    rms = np.asarray(rms, dtype=float)

    if len(rms) == 0:
        return 0.0, np.zeros(0, dtype=bool)

    finite = rms[np.isfinite(rms)]

    if len(finite) == 0:
        return 0.0, np.zeros(len(rms), dtype=bool)

    peak = float(np.max(finite))

    if peak <= 1e-7:
        return 1e-7, np.zeros(len(rms), dtype=bool)

    # Noise estimate.
    noise_floor = _safe_percentile(
        finite,
        10,
        default=0.0,
    )

    # A relative threshold also handles quiet microphones.
    relative_gate = peak * 0.035

    # Keep a small absolute floor.
    absolute_floor = 10 ** (-50 / 20)

    threshold = max(
        absolute_floor,
        noise_floor * 2.5,
        relative_gate,
    )

    active = rms >= threshold

    # Do not allow the activity detector to mark everything as inactive
    # just because the recording is quiet.
    if np.mean(active) < 0.05 and peak > absolute_floor * 2:
        relaxed_gate = max(
            absolute_floor,
            peak * 0.015,
        )

        active = rms >= relaxed_gate
        threshold = relaxed_gate

    return float(threshold), active


def _smooth_boolean_mask(mask, min_run_frames=3):
    """
    Remove very short true/false islands from an activity mask.

    This prevents individual pYIN/RMS frame fluctuations from becoming
    feedback events.
    """

    mask = np.asarray(mask, dtype=bool).copy()

    if len(mask) < 2:
        return mask

    # Fill short false gaps between active regions.
    i = 0

    while i < len(mask):
        if mask[i]:
            i += 1
            continue

        start = i

        while i < len(mask) and not mask[i]:
            i += 1

        end = i

        if (
            start > 0
            and end < len(mask)
            and (end - start) <= min_run_frames
        ):
            mask[start:end] = True

    # Remove very short active islands.
    i = 0

    while i < len(mask):
        if not mask[i]:
            i += 1
            continue

        start = i

        while i < len(mask) and mask[i]:
            i += 1

        end = i

        if (
            start > 0
            and end < len(mask)
            and (end - start) <= min_run_frames
        ):
            mask[start:end] = False

    return mask


# ---------------------------------------------------------------------------
# Pitch tracking
# ---------------------------------------------------------------------------

def _pitch_track_fallback(y, sr):
    """
    Dependency-light fallback pitch detector.

    This is only a backup. The normal production path uses librosa.pyin.
    """

    fmin = MIN_F0
    fmax = min(
        MAX_F0,
        max(MIN_F0 + 100.0, sr * 0.45),
    )

    min_period = max(
        2,
        int(sr / fmax),
    )

    max_period = min(
        FRAME // 2,
        int(sr / fmin),
    )

    f0_list = []
    vf_list = []

    window = np.hanning(FRAME)

    for start in range(
        0,
        max(0, len(y) - FRAME + 1),
        HOP,
    ):
        frame = y[start:start + FRAME]

        if len(frame) < FRAME:
            break

        frame = frame - np.mean(frame)

        energy = float(
            np.mean(np.square(frame))
        )

        if energy < 1e-7:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        weighted = frame * window

        corr = np.correlate(
            weighted,
            weighted,
            mode="full",
        )[FRAME - 1:]

        if len(corr) <= max_period:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        if corr[0] <= 1e-12:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        corr_norm = corr / (corr[0] + 1e-12)

        d = 2.0 * (
            corr_norm[0]
            - corr_norm[min_period:max_period + 1]
        )

        if len(d) == 0:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        cumulative = np.cumsum(d)
        indexes = np.arange(
            1,
            len(d) + 1,
        )

        cmnd = np.where(
            cumulative > 1e-12,
            d * indexes / (cumulative + 1e-12),
            1.0,
        )

        candidates = np.where(
            cmnd < 0.20
        )[0]

        if len(candidates):
            tau = int(candidates[0]) + min_period
        else:
            tau = int(np.argmin(cmnd)) + min_period

        if tau <= 0 or tau >= len(corr_norm):
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        voiced = (
            len(candidates) > 0
            or float(np.min(cmnd)) < 0.30
        )

        if not voiced:
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        f0 = sr / float(tau)

        if not (
            MIN_F0 <= f0 <= MAX_F0
        ):
            f0_list.append(np.nan)
            vf_list.append(False)
            continue

        f0_list.append(f0)
        vf_list.append(True)

    if not f0_list:
        return (
            np.array([], dtype=float),
            np.array([], dtype=bool),
        )

    f0 = np.asarray(
        f0_list,
        dtype=float,
    )

    voiced = np.asarray(
        vf_list,
        dtype=bool,
    )

    return f0, voiced


def _remove_pitch_outliers(f0, voiced_flag):
    """
    Remove obvious octave jumps and isolated pitch outliers.

    This is important because a single 2x/0.5x pYIN error can massively
    distort a cents-based pitch stability score.
    """

    f0 = np.asarray(
        f0,
        dtype=float,
    ).copy()

    voiced = np.asarray(
        voiced_flag,
        dtype=bool,
    ).copy()

    n = min(
        len(f0),
        len(voiced),
    )

    f0 = f0[:n]
    voiced = voiced[:n]

    valid = (
        voiced
        & np.isfinite(f0)
        & (f0 >= MIN_F0)
        & (f0 <= MAX_F0)
    )

    f0[~valid] = np.nan
    voiced = valid

    if np.sum(valid) < 5:
        return f0, voiced

    # First remove isolated octave jumps using local neighbors.
    for i in range(1, len(f0) - 1):

        if not (
            voiced[i - 1]
            and voiced[i]
            and voiced[i + 1]
        ):
            continue

        previous = f0[i - 1]
        current = f0[i]
        following = f0[i + 1]

        if not (
            np.isfinite(previous)
            and np.isfinite(current)
            and np.isfinite(following)
        ):
            continue

        median_neighbor = float(
            np.median([
                previous,
                following,
            ])
        )

        if median_neighbor <= 0:
            continue

        ratio = current / median_neighbor

        # Strong octave relationship.
        if (
            ratio > 1.75
            or ratio < 0.57
        ):
            f0[i] = median_neighbor

    # Rolling median removes remaining isolated spikes.
    smoothed = _median_filter_1d(
        f0,
        radius=2,
    )

    # Only replace points that are not wildly different from the local
    # median. This preserves natural vibrato.
    for i in range(len(f0)):

        if not voiced[i]:
            continue

        local_start = max(
            0,
            i - 2,
        )

        local_end = min(
            len(f0),
            i + 3,
        )

        local = f0[local_start:local_end]

        local = local[
            np.isfinite(local)
        ]

        if len(local) < 3:
            continue

        local_median = float(
            np.median(local)
        )

        if local_median <= 0:
            continue

        ratio = f0[i] / local_median

        if (
            ratio > 1.65
            or ratio < 0.60
        ):
            f0[i] = smoothed[i]

    return f0, voiced


def _pitch_track(y, sr, rms=None):
    """
    Return:

        f0_hz
        voiced_flag

    using pYIN when available.
    """

    if rms is None:
        rms = _rms_track(y)

    if LIBROSA_OK:

        try:
            fmin = max(
                librosa.note_to_hz("C2"),
                MIN_F0,
            )

            fmax = min(
                librosa.note_to_hz("C7"),
                MAX_F0,
                sr * 0.45,
            )

            if fmax <= fmin:
                fmax = min(
                    sr * 0.45,
                    MIN_F0 + 600,
                )

            f0, voiced_flag, voiced_prob = librosa.pyin(
                y,
                fmin=fmin,
                fmax=fmax,
                sr=sr,
                hop_length=HOP,
                frame_length=FRAME,
                fill_na=np.nan,
            )

            f0 = np.asarray(
                f0,
                dtype=float,
            )

            voiced_flag = np.asarray(
                voiced_flag,
                dtype=bool,
            )

            voiced_prob = np.asarray(
                voiced_prob,
                dtype=float,
            )

            n = min(
                len(f0),
                len(voiced_flag),
                len(voiced_prob),
                len(rms),
            )

            f0 = f0[:n]
            voiced_flag = voiced_flag[:n]
            voiced_prob = voiced_prob[:n]

            # Energy gate.
            _, active = _energy_gate(
                rms[:n]
            )

            # pYIN can be uncertain at very quiet frames.
            # Do not accept those frames as reliable pitch.
            reliable = (
                voiced_flag
                & np.isfinite(f0)
                & (voiced_prob >= 0.45)
                & active
            )

            f0[~reliable] = np.nan
            voiced_flag = reliable

            f0, voiced_flag = _remove_pitch_outliers(
                f0,
                voiced_flag,
            )

            return f0, voiced_flag

        except Exception:
            pass

    # Fallback path
    f0, voiced = _pitch_track_fallback(
        y,
        sr,
    )

    if len(rms):
        _, active = _energy_gate(rms)

        n = min(
            len(f0),
            len(voiced),
            len(active),
        )

        f0 = f0[:n]
        voiced = (
            voiced[:n]
            & active[:n]
        )

        f0[~voiced] = np.nan

    return _remove_pitch_outliers(
        f0,
        voiced,
    )


# ---------------------------------------------------------------------------
# Pitch scoring
# ---------------------------------------------------------------------------

def _pitch_stability(f0):
    """
    Robust pitch stability score.

    Uses median absolute deviation rather than raw standard deviation.
    This prevents one bad pYIN frame from destroying the entire score.

    Natural vibrato is therefore treated more gently.
    """

    f0 = np.asarray(
        f0,
        dtype=float,
    )

    voiced = f0[
        np.isfinite(f0)
        & (f0 >= MIN_F0)
        & (f0 <= MAX_F0)
    ]

    if len(voiced) < MIN_VOICED_FRAMES:
        return 50

    # Work in cents around a local median.
    window_size = max(
        12,
        len(voiced) // 5,
    )

    deviations = []

    for start in range(
        0,
        len(voiced),
        window_size,
    ):

        segment = voiced[
            start:start + window_size
        ]

        if len(segment) < 5:
            continue

        median_pitch = float(
            np.median(segment)
        )

        if median_pitch <= 0:
            continue

        cents = (
            1200.0
            * np.log2(
                np.clip(
                    segment / median_pitch,
                    0.5,
                    2.0,
                )
            )
        )

        median_cents = float(
            np.median(cents)
        )

        mad = float(
            np.median(
                np.abs(
                    cents
                    - median_cents
                )
            )
        )

        # Convert MAD to an approximate robust standard deviation.
        robust_std = mad * 1.4826

        deviations.append(
            robust_std
        )

    if not deviations:
        return 50

    pitch_error = float(
        np.median(deviations)
    )

    # Conservative scoring:
    #
    # <= 8 cents   excellent
    # 15 cents     very good
    # 30 cents     acceptable
    # 50 cents     needs work
    # 80+ cents    poor
    score = np.interp(
        pitch_error,
        [
            5,
            10,
            20,
            35,
            55,
            80,
            120,
        ],
        [
            97,
            94,
            86,
            75,
            60,
            40,
            20,
        ],
    )

    return int(
        np.clip(
            score,
            0,
            100,
        )
    )


# ---------------------------------------------------------------------------
# Vocal energy / consistency scoring
# ---------------------------------------------------------------------------

def _vocal_energy_score(rms, active_mask):
    """
    Score steadiness of vocal energy.

    Important:
        This is NOT a measurement of physical airflow.

    It measures microphone-recorded vocal energy consistency.
    """

    rms = np.asarray(
        rms,
        dtype=float,
    )

    active_mask = np.asarray(
        active_mask,
        dtype=bool,
    )

    n = min(
        len(rms),
        len(active_mask),
    )

    if n == 0:
        return 50

    active_rms = rms[:n][
        active_mask[:n]
    ]

    active_rms = active_rms[
        np.isfinite(active_rms)
        & (active_rms > 1e-7)
    ]

    if len(active_rms) < 5:
        return 60

    median_rms = float(
        np.median(active_rms)
    )

    if median_rms <= 1e-8:
        return 50

    # Robust variation instead of standard deviation.
    q25 = float(
        np.percentile(
            active_rms,
            25,
        )
    )

    q75 = float(
        np.percentile(
            active_rms,
            75,
        )
    )

    robust_cv = (
        (q75 - q25)
        / (2.0 * median_rms + 1e-9)
    )

    score = np.interp(
        robust_cv,
        [
            0.02,
            0.06,
            0.12,
            0.20,
            0.32,
            0.50,
        ],
        [
            98,
            94,
            87,
            75,
            58,
            35,
        ],
    )

    return int(
        np.clip(
            score,
            0,
            100,
        )
    )


def _breath_support(rms, voiced_flag):
    """
    Backward-compatible name.

    The microphone cannot directly measure diaphragm airflow.
    Therefore this score represents vocal-energy steadiness and
    sustained vocal presence.
    """

    n = min(
        len(rms),
        len(voiced_flag),
    )

    if n == 0:
        return 50

    rms = np.asarray(
        rms[:n],
        dtype=float,
    )

    voiced_flag = np.asarray(
        voiced_flag[:n],
        dtype=bool,
    )

    _, active = _energy_gate(
        rms
    )

    useful = (
        voiced_flag
        | active
    )

    return _vocal_energy_score(
        rms,
        useful,
    )


# ---------------------------------------------------------------------------
# Continuity / gap detection
# ---------------------------------------------------------------------------

def _gap_mask(rms, voiced_flag, sr):
    """
    Detect genuine silence/gap candidates.

    A frame is considered part of a gap only when:
        1. audio energy is genuinely low
        2. pYIN does not detect a voiced signal
        3. the low-energy region persists

    This avoids turning a single pYIN uncertainty into "Gap detected".
    """

    n = min(
        len(rms),
        len(voiced_flag),
    )

    if n == 0:
        return np.zeros(0, dtype=bool)

    rms = np.asarray(
        rms[:n],
        dtype=float,
    )

    voiced_flag = np.asarray(
        voiced_flag[:n],
        dtype=bool,
    )

    _, active = _energy_gate(
        rms
    )

    # Estimate the typical vocal energy.
    voiced_rms = rms[
        voiced_flag
        & np.isfinite(rms)
        & (rms > 1e-7)
    ]

    if len(voiced_rms) < 5:
        voiced_rms = rms[
            active
            & np.isfinite(rms)
            & (rms > 1e-7)
        ]

    if len(voiced_rms) == 0:
        return np.zeros(
            n,
            dtype=bool,
        )

    typical_energy = float(
        np.median(voiced_rms)
    )

    if typical_energy <= 1e-8:
        return np.zeros(
            n,
            dtype=bool,
        )

    # A real gap should be substantially quieter than the singing.
    silence_threshold = max(
        typical_energy * 0.13,
        10 ** (-50 / 20),
    )

    low_energy = rms < silence_threshold

    candidate = (
        low_energy
        & ~voiced_flag
    )

    # Convert minimum gap duration to frames.
    frames_required = max(
        3,
        int(
            MIN_GAP_SECONDS
            * sr
            / HOP
        ),
    )

    candidate = _smooth_boolean_mask(
        candidate,
        min_run_frames=2,
    )

    # Keep only runs long enough to represent an actual gap.
    final = np.zeros(
        n,
        dtype=bool,
    )

    i = 0

    while i < n:

        if not candidate[i]:
            i += 1
            continue

        start = i

        while (
            i < n
            and candidate[i]
        ):
            i += 1

        end = i

        if (
            end - start
            >= frames_required
        ):
            final[start:end] = True

    return final


def _continuity(
    voiced_flag,
    rms=None,
    sr=None,
):
    """
    Continuity score based on actual sustained gaps, not every
    pYIN unvoiced frame.
    """

    if len(voiced_flag) == 0:
        return 50

    if rms is None or sr is None:
        # Conservative fallback.
        voiced_ratio = float(
            np.mean(voiced_flag)
        )

        return int(
            np.clip(
                voiced_ratio * 100,
                30,
                96,
            )
        )

    gaps = _gap_mask(
        rms,
        voiced_flag,
        sr,
    )

    gap_ratio = (
        float(np.mean(gaps))
        if len(gaps)
        else 0.0
    )

    # Start from a high score and penalize sustained gaps.
    score = 96.0 - (
        gap_ratio * 180.0
    )

    # If almost no voice was detected, don't pretend continuity was good.
    voiced_ratio = float(
        np.mean(voiced_flag)
    )

    if voiced_ratio < 0.15:
        score -= 25

    elif voiced_ratio < 0.30:
        score -= 10

    return int(
        np.clip(
            score,
            20,
            98,
        )
    )


# ---------------------------------------------------------------------------
# Onset scoring
# ---------------------------------------------------------------------------

def _onset_smoothness(y, sr):
    """
    Estimate onset smoothness from changes in recorded vocal energy.

    This is an acoustic measurement, not a physiological measurement.
    """

    if not LIBROSA_OK:
        return 70

    try:
        rms = _rms_track(y)

        if len(rms) < 8:
            return 70

        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            hop_length=HOP,
            backtrack=False,
        )

        if len(onset_frames) == 0:
            return 75

        scores = []

        for frame in onset_frames:

            frame = int(frame)

            before_start = max(
                0,
                frame - 5,
            )

            before_end = frame

            after_start = frame

            after_end = min(
                len(rms),
                frame + 5,
            )

            before = rms[
                before_start:before_end
            ]

            after = rms[
                after_start:after_end
            ]

            if len(after) == 0:
                continue

            pre = float(
                np.median(before)
            ) if len(before) else 0.0

            post = float(
                np.median(after)
            )

            if post <= 1e-7:
                continue

            rise = (
                post - pre
            ) / post

            rise = float(
                np.clip(
                    rise,
                    0.0,
                    1.0,
                )
            )

            # Very abrupt rise = lower score.
            onset_score = np.interp(
                rise,
                [
                    0.05,
                    0.20,
                    0.40,
                    0.65,
                    0.85,
                    1.00,
                ],
                [
                    96,
                    94,
                    88,
                    76,
                    58,
                    40,
                ],
            )

            scores.append(
                onset_score
            )

        if not scores:
            return 72

        return int(
            np.clip(
                np.median(scores),
                0,
                100,
            )
        )

    except Exception:
        return 70


# ---------------------------------------------------------------------------
# Spectral helpers (Level 3+)
# ---------------------------------------------------------------------------

def _spectral_centroid_track(y, sr):
    if LIBROSA_OK:
        try:
            sc = librosa.feature.spectral_centroid(y=y, sr=sr, hop_length=HOP, n_fft=FRAME)[0]
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


def _spectral_flatness_track(y):
    if LIBROSA_OK:
        try:
            sf = librosa.feature.spectral_flatness(y=y, hop_length=HOP, n_fft=FRAME)[0]
            return np.asarray(sf, dtype=np.float64)
        except Exception:
            pass
    n = max(1, int(np.ceil(len(y) / HOP)))
    out = np.zeros(n, dtype=np.float64)
    win = np.hanning(FRAME)
    for i in range(n):
        s, e = i * HOP, min(i * HOP + FRAME, len(y))
        frame = y[s:e]
        if len(frame) < FRAME:
            frame = np.pad(frame, (0, FRAME - len(frame)))
        mag = np.abs(np.fft.rfft(frame * win)) + 1e-10
        geo = float(np.exp(np.mean(np.log(mag))))
        arith = float(np.mean(mag))
        out[i] = geo / (arith + 1e-10)
    return out


def _vowel_consistency_score(y, sr, rms):
    centroid = _spectral_centroid_track(y, sr)
    _, active = _energy_gate(rms)
    n = min(len(centroid), len(active))
    ac = centroid[:n][active[:n]]
    ac = ac[np.isfinite(ac) & (ac > 0)]
    if len(ac) < 5:
        return 60
    med = float(np.median(ac))
    if med < 1.0:
        return 60
    q25 = float(np.percentile(ac, 25))
    q75 = float(np.percentile(ac, 75))
    cv = (q75 - q25) / (2.0 * med + 1e-9)
    score = float(np.interp(cv, [0.02, 0.06, 0.12, 0.22, 0.35, 0.50],
                                [98,   94,   87,   74,   58,   35]))
    return int(np.clip(score, 0, 100))


def _tension_score(y, sr, rms, voiced_flag):
    flatness = _spectral_flatness_track(y)
    _, active = _energy_gate(rms)
    n = min(len(flatness), len(active))
    af = flatness[:n][active[:n]]
    af = af[np.isfinite(af)]
    if len(af) < 5:
        return 65
    flat_score = float(np.interp(
        float(np.median(af)),
        [0.01, 0.04, 0.08, 0.15, 0.25, 0.40],
        [97,   93,   85,   70,   50,   30],
    ))
    energy_score = float(_vocal_energy_score(rms, active))
    return int(np.clip(0.60 * flat_score + 0.40 * energy_score, 0, 100))


def _consonant_clarity_score(y, sr):
    if not LIBROSA_OK:
        return 70
    try:
        rms = _rms_track(y)
        onset_frames = librosa.onset.onset_detect(
            y=y, sr=sr, hop_length=HOP, backtrack=False)
        if len(onset_frames) == 0:
            return 55
        scores = []
        for frame in onset_frames:
            f = int(frame)
            before = rms[max(0, f - 5):f]
            after  = rms[f:min(len(rms), f + 5)]
            if len(after) == 0:
                continue
            pre  = float(np.median(before)) if len(before) else 0.0
            post = float(np.median(after))
            if post <= 1e-7:
                continue
            rise = float(np.clip((post - pre) / post, 0.0, 1.0))
            scores.append(float(np.interp(
                rise,
                [0.05, 0.20, 0.40, 0.65, 0.90, 1.00],
                [40,   65,   85,   92,   78,   60],
            )))
        if not scores:
            return 65
        return int(np.clip(float(np.median(scores)), 0, 100))
    except Exception:
        return 65


def _legato_smoothness_score(f0, voiced_flag, rms, sr):
    cont = _continuity(voiced_flag, rms, sr)
    voiced = f0[np.isfinite(f0) & (f0 >= MIN_F0)]
    if len(voiced) >= 4:
        cents = 1200.0 * np.log2(
            np.clip(voiced[1:] / (voiced[:-1] + 1e-9), 0.5, 2.0))
        smooth = int(np.clip(100 - float(np.mean(np.abs(cents) > 200)) * 300, 20, 100))
    else:
        smooth = 60
    _, active = _energy_gate(rms)
    energy = _vocal_energy_score(rms, active)
    return int(np.clip(0.50 * cont + 0.30 * smooth + 0.20 * energy, 0, 100))


def _breath_phrasing_score(rms, voiced_flag, sr, duration):
    gaps = _gap_mask(rms, voiced_flag, sr)
    if not np.any(gaps):
        return 88, None, "no_breath"
    longest_run = 0
    gap_start_best = 0
    i = 0
    while i < len(gaps):
        if gaps[i]:
            s = i
            while i < len(gaps) and gaps[i]:
                i += 1
            run = i - s
            if run > longest_run:
                longest_run = run
                gap_start_best = s
        else:
            i += 1
    breath_time = float(gap_start_best * HOP / max(sr, 1))
    pct = breath_time / max(duration, 1.0)
    if pct < 0.15 or pct > 0.85:
        return 88, breath_time, "phrase_end"
    elif pct < 0.30 or pct > 0.70:
        return 72, breath_time, "near_phrase_end"
    else:
        return 45, breath_time, "mid_phrase"


# ---------------------------------------------------------------------------
# General metrics
# ---------------------------------------------------------------------------

def _voiced_pct(voiced_flag):
    if len(voiced_flag) == 0:
        return 0.0

    return float(
        np.mean(voiced_flag)
    )


def _voice_presence_score(
    f0,
    voiced_flag,
    active_mask,
):
    """
    Score how much of the recording contains reliable vocal material.

    This is deliberately separated from continuity.
    """

    n = min(
        len(f0),
        len(voiced_flag),
        len(active_mask),
    )

    if n == 0:
        return 0

    reliable_pitch = (
        voiced_flag[:n]
        & np.isfinite(f0[:n])
    )

    active = active_mask[:n]

    reliable_ratio = float(
        np.mean(reliable_pitch)
    )

    active_ratio = float(
        np.mean(active)
    )

    # Reliable vocal frames are more valuable than raw amplitude.
    score = (
        reliable_ratio * 0.75
        + active_ratio * 0.25
    ) * 100.0

    return int(
        np.clip(
            score,
            0,
            100,
        )
    )


# ---------------------------------------------------------------------------
# Exercise scoring
# ---------------------------------------------------------------------------

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
    # Level 3 — Articulation
    "vowel_sustain":      [0.30, 0.40, 0.30],
    "vowel_ascending":    [0.35, 0.30, 0.35],
    "vowel_modification": [0.25, 0.45, 0.30],
    "consonant_clarity":  [0.50, 0.25, 0.25],
    "tongue_tension":     [0.30, 0.40, 0.30],
    "diction_challenge":  [0.35, 0.35, 0.30],
    # Level 4 — Legato & Musical Line
    "legato_notes":       [0.25, 0.50, 0.25],
    "legato_melody":      [0.25, 0.50, 0.25],
    "breath_phrasing":    [0.20, 0.45, 0.35],
    "melodic_etude":      [0.30, 0.40, 0.30],
    # Level 5 — Rhythm
    "metronome_singing":  [0.60, 0.20, 0.20],
    "rhythm_quarters":    [0.65, 0.20, 0.15],
    "rhythm_compound":    [0.65, 0.20, 0.15],
    "clap_sing":          [0.60, 0.20, 0.20],
    "syncopation":        [0.65, 0.20, 0.15],
}


def _subscores(
    y,
    sr,
    f0,
    voiced_flag,
    rms,
    exercise_type,
):
    """
    Generate the three dimensions expected by the current UI.
    """

    _, active = _energy_gate(
        rms
    )

    ps = _pitch_stability(
        f0
    )

    energy = _breath_support(
        rms,
        voiced_flag,
    )

    continuity = _continuity(
        voiced_flag,
        rms,
        sr,
    )

    onset = _onset_smoothness(
        y,
        sr,
    )

    presence = _voice_presence_score(
        f0,
        voiced_flag,
        active,
    )

    table = {

        "warm_up": {
            "Pitch Stability": ps,
            "Breath Support": energy,
            "Consistency": continuity,
        },

        "range_finder": {
            "Range Clarity": ps,
            "Voice Presence": presence,
            "Transitions": continuity,
        },

        "ear_training": {
            "Pitch Accuracy": ps,
            "Intonation": ps,
            "Voice Presence": presence,
        },

        "breath_support": {
            "Airflow Steadiness": energy,
            "Support Duration": continuity,
            "Consistency": energy,
        },

        "silent_breath": {
            "Breath Control": energy,
            "Support Duration": continuity,
            "Consistency": energy,
        },

        "smooth_onset": {
            "Attack Smoothness": onset,
            "Consistency": ps,
            "Tone Quality": energy,
        },

        "legato": {
            "Continuity": continuity,
            "Phrase Shape": ps,
            "Onset Smoothness": onset,
        },

        "scale": {
            "Pitch Accuracy": ps,
            "Evenness": energy,
            "Smoothness": onset,
        },

        "staccato": {
            "Articulation": onset,
            "Pitch Accuracy": ps,
            "Consistency": energy,
        },

        "scale_ascending": {
            "Pitch Accuracy": ps,
            "Evenness": energy,
            "Range": presence,
        },

        "scale_descending": {
            "Pitch Accuracy": ps,
            "Control": energy,
            "Consistency": continuity,
        },

        "minor_scale": {
            "Pitch Accuracy": ps,
            "Tone Quality": energy,
            "Consistency": continuity,
        },

        "intervals": {
            "Interval Accuracy": ps,
            "Intonation": ps,
            "Confidence": presence,
        },

        "arpeggios": {
            "Pitch Accuracy": ps,
            "Agility": onset,
            "Consistency": continuity,
        },

        "pitch_stability": {
            "Pitch Stability": ps,
            "Vibrato Control": max(0, ps - 5),
            "Sustain": continuity,
        },

        # Level 3 — Articulation
        "vowel_sustain": {
            "Vowel Consistency": _vowel_consistency_score(y, sr, rms),
            "Tone Quality":      _tension_score(y, sr, rms, voiced_flag),
            "Pitch Stability":   ps,
        },
        "vowel_ascending": {
            "Pitch Accuracy":    ps,
            "Vowel Consistency": _vowel_consistency_score(y, sr, rms),
            "Continuity":        continuity,
        },
        "vowel_modification": {
            "Pitch Accuracy":    ps,
            "Tone Focus":        _tension_score(y, sr, rms, voiced_flag),
            "Continuity":        continuity,
        },
        "consonant_clarity": {
            "Onset Clarity":     _consonant_clarity_score(y, sr),
            "Pitch Accuracy":    ps,
            "Consistency":       energy,
        },
        "tongue_tension": {
            "Relaxation Score":  _tension_score(y, sr, rms, voiced_flag),
            "Tone Quality":      energy,
            "Continuity":        continuity,
        },
        "diction_challenge": {
            "Articulation":      _consonant_clarity_score(y, sr),
            "Pitch Accuracy":    ps,
            "Continuity":        continuity,
        },

        # Level 4 — Legato & Musical Line
        "legato_notes": {
            "Continuity":        continuity,
            "Phrase Smoothness": _legato_smoothness_score(f0, voiced_flag, rms, sr),
            "Onset Quality":     onset,
        },
        "legato_melody": {
            "Continuity":        continuity,
            "Phrase Smoothness": _legato_smoothness_score(f0, voiced_flag, rms, sr),
            "Pitch Accuracy":    ps,
        },
        "breath_phrasing": {
            "Pitch Accuracy":    ps,
            "Phrase Smoothness": _legato_smoothness_score(f0, voiced_flag, rms, sr),
            "Breath Placement":  _breath_phrasing_score(rms, voiced_flag, sr, 8.0)[0],
        },
        "melodic_etude": {
            "Pitch Accuracy":    ps,
            "Phrase Smoothness": _legato_smoothness_score(f0, voiced_flag, rms, sr),
            "Continuity":        continuity,
        },

        # Level 5 — Rhythm (rhythm exercises use analyze_rhythm_timing; these are fallbacks)
        "metronome_singing": {
            "Pitch Stability": ps,
            "Breath Support":  energy,
            "Consistency":     continuity,
        },
        "rhythm_quarters": {
            "Pitch Stability": ps,
            "Breath Support":  energy,
            "Consistency":     continuity,
        },
        "rhythm_compound": {
            "Pitch Stability": ps,
            "Breath Support":  energy,
            "Consistency":     continuity,
        },
        "clap_sing": {
            "Pitch Stability": ps,
            "Breath Support":  energy,
            "Consistency":     continuity,
        },
        "syncopation": {
            "Pitch Stability": ps,
            "Breath Support":  energy,
            "Consistency":     continuity,
        },
    }

    return table.get(
        exercise_type,
        {
            "Pitch Stability": ps,
            "Breath Support": energy,
            "Consistency": continuity,
        },
    )


def _weighted_score(
    sub,
    exercise_type,
):
    if not sub:
        return 0

    values = list(
        sub.values()
    )

    weights = _WEIGHTS.get(
        exercise_type
    )

    if (
        not weights
        or len(weights) != len(values)
    ):
        weights = [
            1.0 / len(values)
        ] * len(values)

    raw = sum(
        value * weight
        for value, weight
        in zip(values, weights)
    )

    return int(
        np.clip(
            raw,
            0,
            100,
        )
    )


def _xp(score):
    if score >= 90:
        return 150

    if score >= 80:
        return 120

    if score >= 70:
        return 100

    if score >= 60:
        return 80

    return 50


# ---------------------------------------------------------------------------
# Feedback helpers
# ---------------------------------------------------------------------------

def _ts(seconds):
    seconds = max(
        0.0,
        float(seconds),
    )

    return (
        f"{int(seconds // 60)}:"
        f"{int(seconds % 60):02d}"
    )


def _range_notes(f0):
    if not LIBROSA_OK:
        return None, None

    voiced = f0[
        np.isfinite(f0)
    ]

    if len(voiced) < 5:
        return None, None

    try:
        low = librosa.hz_to_note(
            float(
                np.percentile(
                    voiced,
                    5,
                )
            ),
            octave=True,
        )

        high = librosa.hz_to_note(
            float(
                np.percentile(
                    voiced,
                    95,
                )
            ),
            octave=True,
        )

        return low, high

    except Exception:
        return None, None


def _window_pitch_quality(segment):
    """
    Return robust pitch variation in cents.
    """

    voiced = segment[
        np.isfinite(segment)
    ]

    if len(voiced) < 6:
        return None

    median_pitch = float(
        np.median(voiced)
    )

    if median_pitch <= 0:
        return None

    cents = (
        1200.0
        * np.log2(
            np.clip(
                voiced / median_pitch,
                0.5,
                2.0,
            )
        )
    )

    median_cents = float(
        np.median(cents)
    )

    mad = float(
        np.median(
            np.abs(
                cents
                - median_cents
            )
        )
    )

    return mad * 1.4826


def _generate_feedback(
    y,
    sr,
    f0,
    voiced_flag,
    rms,
    times,
    exercise_type,
    duration,
):
    """
    Generate conservative, human-readable feedback.

    Important design change:
        Feedback is only generated when the evidence is strong enough.
    """

    feedback = []

    n = min(
        len(f0),
        len(voiced_flag),
        len(rms),
        len(times),
    )

    if n == 0:
        return feedback

    f0 = f0[:n]
    voiced_flag = voiced_flag[:n]
    rms = rms[:n]
    times = times[:n]

    _, active = _energy_gate(
        rms
    )

    gaps = _gap_mask(
        rms,
        voiced_flag,
        sr,
    )

    # ------------------------------------------------------------------
    # Opening pitch
    # ------------------------------------------------------------------

    all_voiced = f0[
        np.isfinite(f0)
    ]

    if (
        len(all_voiced)
        >= MIN_VOICED_FRAMES
        and LIBROSA_OK
    ):

        try:
            note = librosa.hz_to_note(
                float(
                    np.median(
                        all_voiced
                    )
                ),
                octave=True,
            )

            feedback.append(
                {
                    "time": "0:00",
                    "message": (
                        f"Pitch centres around {note}"
                    ),
                }
            )

        except Exception:
            pass

    # ------------------------------------------------------------------
    # Windowed feedback
    # ------------------------------------------------------------------

    # About 1.5 seconds gives more localized feedback without being
    # hypersensitive to tiny frame-level changes.
    window_seconds = 1.5

    window_frames = max(
        1,
        int(
            window_seconds
            * sr
            / HOP
        ),
    )

    for start in range(
        0,
        n,
        window_frames,
    ):

        end = min(
            start + window_frames,
            n,
        )

        if end - start < 8:
            continue

        mid_index = (
            start
            + (end - start) // 2
        )

        mid_time = float(
            times[
                min(
                    mid_index,
                    len(times) - 1,
                )
            ]
        )

        segment_f0 = f0[
            start:end
        ]

        segment_voiced = voiced_flag[
            start:end
        ]

        segment_rms = rms[
            start:end
        ]

        segment_active = active[
            start:end
        ]

        # --------------------------------------------------------------
        # Pitch feedback
        # --------------------------------------------------------------

        pitch_error = _window_pitch_quality(
            segment_f0
        )

        if pitch_error is not None:

            if pitch_error >= 70:

                feedback.append(
                    {
                        "time": _ts(mid_time),
                        "message": (
                            "Pitch is moving quite a bit "
                            "— try to settle on the target note"
                        ),
                    }
                )

            elif pitch_error >= 42:

                feedback.append(
                    {
                        "time": _ts(mid_time),
                        "message": (
                            "Some pitch drift here "
                            "— try to hold the target more steadily"
                        ),
                    }
                )

            elif (
                pitch_error <= 18
                and np.sum(
                    np.isfinite(segment_f0)
                ) >= 12
            ):

                feedback.append(
                    {
                        "time": _ts(mid_time),
                        "message": (
                            "Pitch is steady here"
                        ),
                    }
                )

        # --------------------------------------------------------------
        # True gap detection
        # --------------------------------------------------------------

        gap_frames = gaps[
            start:end
        ]

        gap_ratio = (
            float(
                np.mean(gap_frames)
            )
            if len(gap_frames)
            else 0.0
        )

        if (
            gap_ratio >= 0.20
            and mid_time > EDGE_IGNORE_SECONDS
            and mid_time < (
                duration
                - EDGE_IGNORE_SECONDS
            )
        ):

            feedback.append(
                {
                    "time": _ts(mid_time),
                    "message": (
                        "A sustained quiet gap was detected "
                        "— try to keep the phrase connected"
                    ),
                }
            )

        # --------------------------------------------------------------
        # Vocal energy feedback
        # --------------------------------------------------------------

        active_rms = segment_rms[
            segment_active
        ]

        active_rms = active_rms[
            np.isfinite(active_rms)
            & (active_rms > 1e-7)
        ]

        if len(active_rms) >= 8:

            median_energy = float(
                np.median(
                    active_rms
                )
            )

            q25 = float(
                np.percentile(
                    active_rms,
                    25,
                )
            )

            q75 = float(
                np.percentile(
                    active_rms,
                    75,
                )
            )

            robust_cv = (
                q75 - q25
            ) / (
                2.0
                * median_energy
                + 1e-9
            )

            if robust_cv >= 0.38:

                feedback.append(
                    {
                        "time": _ts(mid_time),
                        "message": (
                            "Vocal energy is uneven "
                            "— aim for a smoother, steadier volume"
                        ),
                    }
                )

        # --------------------------------------------------------------
        # Avoid too many positive messages.
        # Positive feedback is useful, but the user should primarily
        # receive actionable feedback.
        # --------------------------------------------------------------

    # ------------------------------------------------------------------
    # Range finder
    # ------------------------------------------------------------------

    if exercise_type == "range_finder":

        low, high = _range_notes(
            f0
        )

        if low and high:

            feedback.append(
                {
                    "time": _ts(
                        max(
                            0,
                            duration * 0.90,
                        )
                    ),
                    "message": (
                        f"Detected range: {low} – {high}"
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Warm-up specific feedback
    # ------------------------------------------------------------------

    if exercise_type == "warm_up":
        if duration < 6.0:
            feedback.append(
                {
                    "time": "0:00",
                    "message": (
                        "Hold the exhalation for longer "
                        "— aim for 10–15 seconds"
                    ),
                }
            )
        elif duration >= 10.0:
            feedback.append(
                {
                    "time": "0:00",
                    "message": "Good — you held the exhalation well",
                }
            )

        _, _wu_active = _energy_gate(rms)
        _wu_rms = rms[
            _wu_active
            & np.isfinite(rms)
            & (rms > 1e-7)
        ]

        if len(_wu_rms) >= 8:
            _q25 = float(np.percentile(_wu_rms, 25))
            _q75 = float(np.percentile(_wu_rms, 75))
            _med  = float(np.median(_wu_rms))

            if _med > 1e-8:
                _cv = (_q75 - _q25) / (2.0 * _med + 1e-9)

                if _cv < 0.12 and not any(
                    "steady" in item["message"].lower()
                    or "smooth" in item["message"].lower()
                    for item in feedback
                ):
                    feedback.append(
                        {
                            "time": "0:00",
                            "message": (
                                "Very even airflow "
                                "— your breath support is strong"
                            ),
                        }
                    )
                elif _cv > 0.40 and not any(
                    "uneven" in item["message"].lower()
                    for item in feedback
                ):
                    feedback.append(
                        {
                            "time": "0:00",
                            "message": (
                                "Airflow fluctuates — try to release "
                                "air at a constant, gentle rate"
                            ),
                        }
                    )

    # ------------------------------------------------------------------
    # Exercise-specific guidance
    # ------------------------------------------------------------------

    if exercise_type in {
        "breath_support",
        "silent_breath",
    }:

        if not any(
            "energy" in item["message"].lower()
            for item in feedback
        ):

            feedback.append(
                {
                    "time": "0:00",
                    "message": (
                        "Keep the vocal energy even "
                        "through the sustained phrase"
                    ),
                }
            )

    # ------------------------------------------------------------------
    # Deduplicate
    # ------------------------------------------------------------------

    seen = set()
    cleaned = []

    for item in feedback:

        message = item.get(
            "message",
            "",
        )

        # Deduplicate exact messages.
        key = message.strip().lower()

        if key in seen:
            continue

        seen.add(key)
        cleaned.append(item)

    # Prefer actionable feedback over repeated positive feedback.
    actionable = [
        item
        for item in cleaned
        if any(
            word in item["message"].lower()
            for word in [
                "try",
                "gap",
                "uneven",
                "drift",
                "moving",
                "hold",
                "target",
                "connected",
            ]
        )
    ]

    positive = [
        item
        for item in cleaned
        if item not in actionable
    ]

    result = (
        actionable
        + positive
    )

    return result[
        :MAX_FEEDBACK_ITEMS
    ]


# ---------------------------------------------------------------------------
# Exercise mapping
# ---------------------------------------------------------------------------

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

    # Level 3 — Articulation
    "3.1": "vowel_sustain",
    "3.2": "vowel_ascending",
    "3.3": "vowel_modification",
    "3.4": "consonant_clarity",
    "3.5": "tongue_tension",
    "3.6": "diction_challenge",

    # Level 4 — Legato & Musical Line
    "4.1": "legato_notes",
    "4.2": "legato_melody",
    "4.3": "breath_phrasing",
    "4.4": "melodic_etude",

    # Level 5 — Rhythm
    "5.1": "metronome_singing",
    "5.2": "rhythm_quarters",
    "5.3": "rhythm_compound",
    "5.4": "clap_sing",
    "5.5": "syncopation",
}


def exercise_type_from_id(exercise_id):
    """
    Convert exercise ID such as 0.1 into the internal exercise type.

    Exact matches are preferred to avoid accidental substring matches.
    """

    value = str(
        exercise_id
    ).strip()

    if value in _EXERCISE_TYPE_MAP:
        return _EXERCISE_TYPE_MAP[
            value
        ]

    # Backward compatibility for IDs such as:
    # "0.1 Vocal Warm-Up"
    for key, exercise_type in _EXERCISE_TYPE_MAP.items():

        if value.startswith(key):
            return exercise_type

    # Handle page file IDs like "15_Exercise_3.1_Pure_Italian_Vowels"
    for key, exercise_type in _EXERCISE_TYPE_MAP.items():
        if key in value:
            return exercise_type

    return "warm_up"


# ---------------------------------------------------------------------------
# Public analysis API
# ---------------------------------------------------------------------------

def analyze_audio(
    audio_bytes,
    exercise_type="warm_up",
):
    """
    Analyse recorded audio.

    Returns:

    {
        "score": int,
        "xp": int,
        "feedback": [
            {
                "time": str,
                "message": str
            }
        ],
        "subscores": {
            ...
        },
        "duration": float,
        "pitch_data": {
            "f0": [...],
            "times": [...]
        }
    }
    """

    if not audio_bytes:
        return _short_result(
            "No recording was received."
        )

    # --------------------------------------------------------------
    # Load
    # --------------------------------------------------------------

    y, sr = _load_audio(
        audio_bytes
    )

    if (
        y is None
        or sr is None
        or sr <= 0
        or len(y) == 0
    ):

        return _short_result(
            "The recording could not be analysed. Please try again."
        )

    duration = (
        len(y)
        / float(sr)
    )

    if duration < MIN_RECORDING_SECONDS:

        return _short_result(
            "Recording too short — hold the note for at least 1 second."
        )

    # --------------------------------------------------------------
    # Remove DC offset
    # --------------------------------------------------------------

    y = y - np.mean(y)

    # Prevent extreme values.
    y = np.clip(
        y,
        -1.0,
        1.0,
    )

    # --------------------------------------------------------------
    # RMS first
    # --------------------------------------------------------------

    rms = _rms_track(
        y
    )

    if len(rms) == 0:

        return _short_result(
            "No usable audio signal was detected."
        )

    # --------------------------------------------------------------
    # Pitch
    # --------------------------------------------------------------

    f0, voiced_flag = _pitch_track(
        y,
        sr,
        rms,
    )

    # --------------------------------------------------------------
    # Align all frame arrays
    # --------------------------------------------------------------

    n = min(
        len(f0),
        len(voiced_flag),
        len(rms),
    )

    if n <= 0:

        return _short_result(
            "No usable vocal signal was detected."
        )

    f0 = f0[:n]

    voiced_flag = voiced_flag[
        :n
    ]

    rms = rms[
        :n
    ]

    times = _frames_to_time(
        n,
        sr,
    )

    # --------------------------------------------------------------
    # Subscores
    # --------------------------------------------------------------

    subscores = _subscores(
        y,
        sr,
        f0,
        voiced_flag,
        rms,
        exercise_type,
    )

    score = _weighted_score(
        subscores,
        exercise_type,
    )

    xp = _xp(
        score
    )

    # --------------------------------------------------------------
    # Feedback
    # --------------------------------------------------------------

    feedback = _generate_feedback(
        y,
        sr,
        f0,
        voiced_flag,
        rms,
        times,
        exercise_type,
        duration,
    )

    # --------------------------------------------------------------
    # Compact pitch data for UI waveform
    # --------------------------------------------------------------

    step = max(
        1,
        n // 500,
    )

    pitch_data = {
        "f0": [
            (
                float(value)
                if np.isfinite(value)
                else None
            )
            for value
            in f0[::step]
        ],

        "times": [
            float(value)
            for value
            in times[::step]
        ],
    }

    # --------------------------------------------------------------
    # Diagnostics
    #
    # Extra data is harmless to the current UI and is useful if you
    # later want to display/debug Cloud vs local analysis.
    # --------------------------------------------------------------

    _, active_mask = _energy_gate(
        rms
    )

    reliable_pitch_ratio = (
        float(
            np.mean(
                voiced_flag
            )
        )
        if len(voiced_flag)
        else 0.0
    )

    active_ratio = (
        float(
            np.mean(
                active_mask
            )
        )
        if len(active_mask)
        else 0.0
    )

    return {
        "score": score,
        "xp": xp,
        "feedback": feedback,
        "subscores": subscores,
        "duration": float(
            duration
        ),
        "pitch_data": pitch_data,

        # Optional diagnostics.
        "analysis_meta": {
            "engine": (
                "librosa.pyin"
                if LIBROSA_OK
                else "fallback"
            ),
            "librosa_version": (
                LIBROSA_VERSION
            ),
            "sample_rate": int(
                sr
            ),
            "reliable_pitch_ratio": round(
                reliable_pitch_ratio,
                3,
            ),
            "active_audio_ratio": round(
                active_ratio,
                3,
            ),
        },
    }


# ---------------------------------------------------------------------------
# Short / invalid recording
# ---------------------------------------------------------------------------

def analyze_pitch_match(audio_bytes, reference_hz):
    """
    Compare recorded audio against a reference pitch.

    Parameters
    ----------
    audio_bytes : bytes
        Recorded audio (WAV or any format librosa can load).
    reference_hz : float
        The reference frequency the user was asked to match.

    Returns
    -------
    dict with keys:
        cents_deviation  float | None   positive = sharp, negative = flat
        abs_cents        float | None
        quality          str  "excellent" | "good" | "fair" | "off" | "miss"
                              | "no_pitch" | "too_short" | "no_audio"
        sung_hz          float | None
        score            int  0 – 100
    """

    _empty = {
        "cents_deviation": None,
        "abs_cents": None,
        "quality": "no_audio",
        "sung_hz": None,
        "score": 0,
    }

    if not audio_bytes or not (50.0 <= reference_hz <= 2000.0):
        return _empty

    y, sr = _load_audio(audio_bytes)

    if y is None or sr is None or sr <= 0:
        return _empty

    duration = len(y) / float(sr)

    if duration < MIN_RECORDING_SECONDS:
        return {**_empty, "quality": "too_short"}

    y = y - np.mean(y)
    y = np.clip(y, -1.0, 1.0)

    rms = _rms_track(y)
    f0, voiced_flag = _pitch_track(y, sr, rms)

    voiced = f0[
        np.isfinite(f0)
        & (f0 >= MIN_F0)
        & (f0 <= MAX_F0)
    ]

    if len(voiced) < MIN_VOICED_FRAMES:
        return {**_empty, "quality": "no_pitch"}

    sung_hz = float(np.median(voiced))

    # Allow ±1 octave matching — singer may naturally match in a different
    # octave from the reference if the reference is outside their range.
    candidates = [sung_hz, sung_hz * 2.0, sung_hz * 0.5]
    best_hz = min(
        candidates,
        key=lambda hz: abs(1200.0 * np.log2(hz / reference_hz)),
    )

    cents_dev = float(1200.0 * np.log2(best_hz / reference_hz))
    abs_cents = abs(cents_dev)

    if abs_cents <= 15:
        quality = "excellent"
        score   = int(np.interp(abs_cents, [0.0,  15.0], [100, 88]))
    elif abs_cents <= 30:
        quality = "good"
        score   = int(np.interp(abs_cents, [15.0, 30.0], [88,  74]))
    elif abs_cents <= 50:
        quality = "fair"
        score   = int(np.interp(abs_cents, [30.0, 50.0], [74,  55]))
    elif abs_cents <= 100:
        quality = "off"
        score   = int(np.interp(abs_cents, [50.0, 100.0], [55, 28]))
    else:
        quality = "miss"
        score   = max(0, int(np.interp(abs_cents, [100.0, 200.0], [28, 0])))

    return {
        "cents_deviation": round(float(cents_dev), 1),
        "abs_cents":       round(float(abs_cents), 1),
        "quality":         quality,
        "sung_hz":         round(float(sung_hz),   1),
        "score":           int(np.clip(score, 0, 100)),
    }


def _short_result(
    message=(
        "Recording too short — "
        "hold the note for at least 1 second."
    )
):
    return {
        "score": 0,
        "xp": 0,
        "feedback": [
            {
                "time": "",
                "message": message,
            }
        ],
        "subscores": {},
        "duration": 0.0,
        "pitch_data": {
            "f0": [],
            "times": [],
        },
    }


# ---------------------------------------------------------------------------
# Level 5 — Rhythm helpers
# ---------------------------------------------------------------------------

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


def analyze_rhythm_timing(audio_bytes, bpm=80, beats_per_bar=4, total_bars=4):
    """
    Analyse vocal onset timing against a metronome beat grid.

    Returns standard shape plus timing_data dict.
    """
    def _e(msg):
        return {
            "score": 0, "xp": 0,
            "feedback": [{"time": "0:00", "message": msg}],
            "subscores": {"Timing Accuracy": 0, "Note Presence": 0, "Consistency": 0},
            "duration": 0.0,
            "pitch_data": {"f0": [], "times": []},
            "timing_data": {"onsets_sec": [], "beat_positions": [],
                            "deviations_ms": [], "avg_deviation_ms": 0.0},
        }

    if not audio_bytes:
        return _e("No recording received.")

    y, sr = _load_audio(audio_bytes)
    if y is None:
        return _e("Could not load audio.")

    duration = len(y) / float(sr)
    if duration < MIN_RECORDING_SECONDS:
        return _e("Recording too short — sing for at least 2 seconds.")

    y = y - np.mean(y)
    y = np.clip(y, -1.0, 1.0)

    rms = _rms_track(y)
    f0, voiced_flag = _pitch_track(y, sr, rms)

    presence = float(np.mean(voiced_flag)) if len(voiced_flag) > 0 else 0.0
    note_presence = int(np.clip(presence * 200, 0, 100))

    if LIBROSA_OK:
        try:
            onsets = librosa.onset.onset_detect(
                y=y, sr=sr, hop_length=HOP, backtrack=True, units="time")
        except Exception:
            onsets = np.array([])
    else:
        onsets = np.array([])

    beat_interval = 60.0 / max(bpm, 20)
    beat_positions = np.array([i * beat_interval
                                for i in range(int(total_bars * beats_per_bar))])

    deviations_ms = []
    if len(onsets) > 0 and len(beat_positions) > 0:
        for t in onsets:
            nearest = beat_positions[np.argmin(np.abs(beat_positions - t))]
            deviations_ms.append(abs(float(t) - float(nearest)) * 1000.0)

    if deviations_ms:
        avg_dev = float(np.mean(deviations_ms))
        std_dev = float(np.std(deviations_ms))
        timing_score  = int(np.interp(avg_dev,
            [0, 30, 60, 100, 200, 400], [100, 92, 80, 65, 40, 20]))
        consist_score = int(np.interp(std_dev,
            [0, 20, 50, 100, 200],       [100, 92, 78, 55, 30]))
    else:
        avg_dev = 0.0
        timing_score = consist_score = 50

    overall = int(np.clip(
        0.60 * timing_score + 0.20 * note_presence + 0.20 * consist_score, 0, 100))

    feedback = []
    if avg_dev < 30:
        feedback.append({"time": "0:00", "message": "Excellent timing — right on the beat"})
    elif avg_dev < 60:
        feedback.append({"time": "0:00", "message": "Good timing — small deviations, keep tightening it"})
    elif avg_dev < 100:
        feedback.append({"time": "0:00",
                         "message": f"Timing close — about {avg_dev:.0f} ms off; aim for under 60 ms"})
    else:
        feedback.append({"time": "0:00",
                         "message": f"Timing needs work — about {avg_dev:.0f} ms off; internalize the beat first"})
    if note_presence < 40:
        feedback.append({"time": "0:00",
                         "message": "Pitch not clearly detected — sing a clear, sustained tone"})
    suggested_bpm = max(60, bpm - 10) if overall < 70 else bpm
    feedback.append({"time": "0:00",
                     "message": f"Suggested practice tempo: {suggested_bpm} BPM"})

    n = min(len(f0), len(voiced_flag))
    step = max(1, n // 500)
    times = _frames_to_time(n, sr)

    return {
        "score": overall,
        "xp":    _xp(overall),
        "feedback": feedback,
        "subscores": {
            "Timing Accuracy": timing_score,
            "Note Presence":   note_presence,
            "Consistency":     consist_score,
        },
        "duration":   float(duration),
        "pitch_data": {
            "f0":    [float(v) if np.isfinite(v) else None for v in f0[:n:step]],
            "times": [float(v) for v in times[:n:step]],
        },
        "timing_data": {
            "onsets_sec":       [float(o) for o in onsets],
            "beat_positions":   [float(b) for b in beat_positions],
            "deviations_ms":    deviations_ms,
            "avg_deviation_ms": round(avg_dev, 1),
        },
    }