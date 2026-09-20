"""
Per-exercise configuration for error detection.

Each exercise declares:
  - pitch_movement: "expected" (scales/arpeggios/melodies) or "is_error" (sustained notes)
  - detectors: list of error_id strings this exercise checks for
  - note_count: expected number of distinct notes (where applicable)
  - duration_target_s: expected hold/phrase duration in seconds (where applicable)
"""

# ── pitch_movement classification ─────────────────────────────────────────
#
# "expected"  — pitch changes are part of the written task
# "is_error"  — the singer should hold a steady pitch; movement = mistake
#
# 2.6 Pitch Stability, 3.1 Pure Italian Vowels, 3.5 Releasing Tongue Tension
#   → sustained-note exercises → "is_error"
# 3.4 Consonant Clarity — repeated syllables on one pitch → "is_error"
# 3.6 Diction Challenge — Phase 2 is a sung descending scale → "expected"
# All scale/arpeggio/melody exercises → "expected"

EXERCISE_CONFIG = {

    # ── Level 1 ───────────────────────────────────────────────────────────
    "1.5": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 2, 4, 5, 7],
        "detectors": [
            "L1_RUSHING_TEMPO",
            "L1_BREATH_DROPOUT",
            "L1_PITCH_FLAT_LATER",
            "L1_UNEVEN_VOLUME",
            "L1_AUDIBLE_GASP",
        ],
    },
    "1.6": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 2, 4, 5, 7],
        "has_parts": True,
        "detectors": [
            "L1_STACCATO_NOT_SEPARATED",
            "L1_LEGATO_BREAKS",
            "L1_STACCATO_TOO_LONG",
            "L1_STACCATO_PITCH_INACCURATE",
            "L1_NO_CONTRAST",
        ],
    },

    # ── Level 2 ───────────────────────────────────────────────────────────
    "2.1": {
        "pitch_movement": "expected",
        "note_count": 8,
        "pattern_semitones": [0, 2, 4, 5, 7, 9, 11, 12],
        "detectors": [
            "L2_PITCH_FLAT_TOP",
            "L2_PUSHING_HIGH",
            "L2_UNEVEN_TEMPO",
            "L2_SCOOPING",
            "L2_MID_SCALE_BREATH",
        ],
    },
    "2.2": {
        "pitch_movement": "expected",
        "note_count": 8,
        "pattern_semitones": [12, 11, 9, 7, 5, 4, 2, 0],
        "detectors": [
            "L2_PITCH_SAG_DESCENDING",
            "L2_VOLUME_FADE_BOTTOM",
            "L2_START_UNSUPPORTED",
            "L2_TONE_DARKENS",
            "L2_FINAL_LESS_ACCURATE",
        ],
    },
    "2.3": {
        "pitch_movement": "expected",
        "note_count": 8,
        "pattern_semitones": [0, 2, 3, 5, 7, 8, 10, 12],
        "detectors": [
            "L2_MAJORIZING",
            "L2_HALFSTEP_WIDE",
            "L2_KEY_CENTER_DRIFT",
            "L2_SUPPORT_DROPS",
        ],
    },
    "2.4": {
        "pitch_movement": "expected",
        "note_count": 2,
        "detectors": [
            "L2_LEAP_OVERSHOOT",
            "L2_SLIDING_LEAP",
            "L2_BREATH_CATCH",
            "L2_SECOND_NOTE_WEAKER",
        ],
    },
    "2.5": {
        "pitch_movement": "expected",
        "note_count": 7,
        "pattern_semitones": [0, 4, 7, 12, 7, 4, 0],
        "detectors": [
            "L2_VOCAL_CRACK",
            "L2_CHEST_TOO_HIGH",
            "L2_TONE_COLOR_CHANGES",
            "L2_UNEVEN_VOLUME_LEAPS",
        ],
    },
    "2.6": {
        "pitch_movement": "is_error",
        "duration_target_s": 7.0,
        "detectors": [
            "L2_PITCH_DRIFT_FLAT",
            "L2_PITCH_WAVER",
            "L2_VOLUME_DECREASE",
            "L2_SHORT_DURATION",
            "L2_SLOW_ONSET",
        ],
    },

    # ── Level 3 ───────────────────────────────────────────────────────────
    "3.1": {
        "pitch_movement": "is_error",
        "duration_target_s": 3.5,
        "vowel_rounds": ["A", "E", "I", "O", "U"],
        "detectors": [
            "L3_VOWEL_DIPHTHONG",
            "L3_WRONG_VOWEL_COLOR",
            "L3_MOUTH_SHIFT",
            "L3_DURATION_INCONSISTENT",
        ],
    },
    "3.2": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 2, 4, 5, 7],
        "detectors": [
            "L3_VOWEL_COLLAPSE",
            "L3_JAW_TIGHTENS",
            "L3_FIRST_LAST_MISMATCH",
            "L3_SUPPORT_DROPS_TOP",
        ],
    },
    "3.3": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 2, 4, 5, 7],
        "detectors": [
            "L3_NO_MODIFICATION",
            "L3_OVER_MODIFICATION",
            "L3_MODIFICATION_MISTIMED",
            "L3_CRACK_DESPITE_MOD",
        ],
    },
    "3.4": {
        "pitch_movement": "is_error",
        "consonant_rounds": ["Na", "Ma", "La", "Ra"],
        "reps_per_round": 5,
        "detectors": [
            "L3_BLURRY_CONSONANT",
            "L3_CLARITY_FADES",
            "L3_VOWEL_SHIFTS_ROUNDS",
            "L3_R_OVER_ARTICULATED",
        ],
    },
    "3.5": {
        "pitch_movement": "is_error",
        "duration_target_s": 5.0,
        "vowel_sequence": ["ah", "ee", "oo"],
        "detectors": [
            "L3_THROATY_TONE",
            "L3_JAW_TENSION",
            "L3_TENSION_VARIES",
            "L3_STRAIN_PITCH",
        ],
    },
    "3.6": {
        "pitch_movement": "expected",
        "has_phases": True,
        "pattern_semitones": [12, 11, 9, 7, 5, 4, 2, 0],
        "detectors": [
            "L3_CONSONANTS_SOFTEN_SUNG",
            "L3_ENDING_CONSONANTS_DROPPED",
            "L3_VOWEL_CROWDS_CONSONANT",
            "L3_SUNG_DICTION_SOFTER",
        ],
    },

    # ── Level 4 ───────────────────────────────────────────────────────────
    "4.1": {
        "pitch_movement": "expected",
        "note_count": 3,
        "pattern_semitones": [0, 2, 4],
        "detectors": [
            "L4_GLOTTAL_STOP",
            "L4_BREATH_PULSE",
            "L4_VOWEL_VOLUME_CHANGE",
            "L4_MID_PHRASE_BREATH",
        ],
    },
    "4.2": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 2, 4, 2, 0],
        "detectors": [
            "L4_BUMPS_AT_CHANGE",
            "L4_NO_DYNAMIC_ARC",
            "L4_ARC_OVERDONE",
            "L4_GLOTTAL_STOP_TRANSITION",
        ],
    },
    "4.3": {
        "pitch_movement": "expected",
        "breath_point_bar": 2,
        "total_bars": 4,
        "detectors": [
            "L4_BREATH_MID_BAR",
            "L4_RAN_OUT_BEFORE_BAR2",
            "L4_STRAINED_THROUGH",
            "L4_CLEAN_SINGLE_BREATH",
        ],
    },
    "4.4": {
        "pitch_movement": "expected",
        "total_bars": 8,
        "breath_points_bars": [4, 8],
        "detectors": [
            "L4_BREATH_WRONG_POINT",
            "L4_ENERGY_TRAILS_OFF",
            "L4_VOWEL_SHIFTS_PEAKS",
            "L4_CLIMAX_NOT_REACHED",
            "L4_ROUGH_TRANSITIONS",
        ],
    },
    "4.5": {
        "pitch_movement": "expected",
        "note_count": 5,
        "pattern_semitones": [0, 4, 7, 4, 0],
        "detectors": [
            "L4_REATTACK_SKIPS",
            "L4_NO_DYNAMIC_SHAPING",
            "L4_VOWEL_SWITCHES",
            "L4_BREATH_FAILS_FINAL",
        ],
    },
}


def get_exercise_config(exercise_id):
    """Return config for the given exercise numeric ID (e.g. '2.1')."""
    clean = str(exercise_id).strip()
    if clean in EXERCISE_CONFIG:
        return EXERCISE_CONFIG[clean]
    for key in EXERCISE_CONFIG:
        if key in clean:
            return EXERCISE_CONFIG[key]
    return None


def pitch_movement_flag(exercise_id):
    """Return 'expected' or 'is_error' for an exercise ID."""
    cfg = get_exercise_config(exercise_id)
    if cfg:
        return cfg["pitch_movement"]
    return "expected"


# ── Detection thresholds ──────────────────────────────────────────────────
# All named constants from the spec, used by detector functions.

THRESHOLDS = {
    # Pitch (all in cents)
    "pitch_accuracy_cents": 25,
    "pitch_flat_progressive_start_cents": 10,
    "pitch_flat_progressive_end_cents": 30,
    "pitch_drift_cents": 20,
    "pitch_waver_sd_cents": 15,
    "scooping_ms": 150,
    "slow_onset_ms": 200,
    "half_step_expected_cents": 100,
    "half_step_too_wide_cents": 130,
    "majorizing_cents": 70,
    "interval_overshoot_cents": 30,

    # Timing
    "note_duration_short_pct": 0.70,
    "staccato_gap_min_ms": 100,
    "staccato_max_duration_pct": 0.40,
    "contrast_gap_diff_ms": 50,
    "tempo_deviation_pct": 0.20,
    "mid_phrase_gap_ms": 200,

    # RMS / energy (dB)
    "breath_dropout_db": 6,
    "uneven_volume_db": 8,
    "pushing_spike_db": 10,
    "volume_fade_db": 8,
    "rms_arc_range_db": 6,

    # Spectral
    "spectral_centroid_drop_pct": 0.25,
    "formant_shift_threshold_hz": 150,
    "formant_diphthong_shift_hz": 100,
    "spectral_tilt_change_db": 4,

    # Onset / consonant
    "consonant_onset_max_ms": 80,
    "glottal_stop_max_ms": 50,
    "vowel_consonant_ratio_min": 0.10,

    # Duration
    "sustain_target_s": 7.0,
    "vowel_duration_variance_pct": 0.20,

    # Formant targets for pure Italian vowels (approximate F1, F2 in Hz)
    "vowel_formants": {
        "A": (800, 1200),
        "E": (500, 1800),
        "I": (300, 2300),
        "O": (500, 900),
        "U": (350, 700),
    },
}
