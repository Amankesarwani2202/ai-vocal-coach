import numpy as np

def evaluate_diaphragmatic_support(processor):
    times, pitches = processor.get_pitch_contour()
    stability = processor.analyze_stability()
    duration = processor.duration
    
    score = 0
    feedback = []
    
    # Check duration
    if duration >= 5.0:
        score += 40
        feedback.append("✅ Great breath capacity! You sustained the note well.")
    elif duration >= 3.0:
        score += 25
        feedback.append("⚠️ Good start, but try to sustain the airflow longer (aim for 5+ seconds).")
    else:
        score += 10
        feedback.append("❌ Very short duration. Focus on slow, controlled release of air.")

    # Check stability
    if stability > 0.7:
        score += 40
        feedback.append("✅ Excellent amplitude consistency. Your support is rock solid.")
    else:
        score += 20
        feedback.append("⚠️ Your airflow is fluctuating. Try to keep the pressure steady from your diaphragm.")
        
    # Check breath spikes (RMS derivative)
    rms_diff = np.diff(processor.rms)
    if np.max(np.abs(rms_diff)) > 0.15:
        score += 10
        feedback.append("❌ Sudden spikes detected. Avoid pushing air out forcefully.")
    else:
        score += 20
        
    return min(score, 100), feedback, {
        "Duration": min((duration/5)*100, 100),
        "Stability": stability * 100,
        "Control": min(score + 10, 100)
    }

def evaluate_scale(processor):
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]
    
    if len(valid_pitches) < 10:
        return 0, ["❌ Not enough pitch data detected. Please sing louder."], {"Pitch":0, "Stability":0, "Control":0}
        
    pitch_std = np.std(valid_pitches)
    
    score = 0
    feedback = []
    
    if pitch_std > 50:
        score += 80
        feedback.append("✅ Good pitch variation across the scale.")
    else:
        score += 40
        feedback.append("⚠️ Your notes sounded very monotone. Make sure you are shifting pitch clearly.")
        
    stability = processor.analyze_stability()
    if stability > 0.6:
        score += 20
        feedback.append("✅ Volume was consistent across different notes.")
    else:
        score += 10
        feedback.append("⚠️ You lost breath support as the pitch changed.")
        
    return min(score, 100), feedback, {
        "Pitch Accuracy": min(pitch_std, 100),
        "Stability": stability * 100,
        "Control": min((score / 100) * 80, 100)
    }

# Generic evaluator for the other exercises to maintain constraints
def evaluate_generic(processor, exercise_type="onset"):
    stability = processor.analyze_stability()
    score = int(stability * 100)
    return score, ["✅ Good effort! Focus on smooth transitions and breath control."], {
        "Control": score, "Breath": 85, "Tone": 90
    }


def evaluate_warm_up(processor):
    """Level 0.1: Warm-up recording evaluation."""
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]
    stability = processor.analyze_stability()
    breathiness = processor.analyze_breathiness()

    score = 0
    feedback = []

    if len(valid_pitches) < 10:
        return 0, ["❌ Not enough pitch detected. Please sing louder and clearer."], {
            "Pitch": 0,
            "Breath": 0,
            "Tone": 0,
        }

    pitch_consistency = 1.0 - min(np.std(valid_pitches) / (np.mean(valid_pitches) + 1e-6), 1.0)

    if pitch_consistency > 0.6:
        score += 40
        feedback.append("✅ Your pitch is quite consistent.")
    else:
        score += 15
        feedback.append("⚠️ Your pitch is wavering. Focus on steady tone.")

    if stability > 0.65:
        score += 35
        feedback.append("✅ Great breath support! Volume is steady.")
    else:
        score += 15
        feedback.append("⚠️ Try to maintain consistent air pressure.")

    if breathiness < 0.3:
        score += 25
        feedback.append("✅ Nice clear tone, not too breathy.")
    else:
        score += 10
        feedback.append("⚠️ Your tone is breathy. Focus on pure vowels.")

    return min(score, 100), feedback, {
        "Pitch Consistency": pitch_consistency * 100,
        "Breath Support": stability * 100,
        "Tone Quality": (1.0 - min(breathiness, 1.0)) * 100,
    }


def evaluate_range_finder(processor):
    """Level 0.2: Range finder evaluation."""
    min_pitch, max_pitch, min_note, max_note = processor.detect_range()

    if min_pitch is None:
        return 0, ["❌ Could not detect your vocal range. Please sing a full ascending scale."], {
            "Range": 0
        }

    range_semitones = 12 * np.log2(max_pitch / min_pitch)
    score = int(min(60 + (range_semitones / 24) * 40, 100))

    feedback = [
        f"✅ Detected range: {min_note} to {max_note} ({range_semitones:.1f} semitones).",
    ]

    if range_semitones < 12:
        feedback.append("⚠️ Your range seems limited. Keep practicing to expand it.")
    else:
        feedback.append("✅ Nice range! That's a good foundation to build on.")

    return score, feedback, {"Range": score}


def evaluate_ear_training(processor, target_freq):
    """Level 0.3: Ear training (match-the-note) evaluation."""
    cents_off = processor.measure_pitch_accuracy(target_freq)
    voiced_pct = processor.detect_voiced_frames()

    if cents_off is None or voiced_pct < 20:
        return 0, ["❌ Not enough singing detected. Please try again."], {"Accuracy": 0}

    accuracy = max(0, 100 - abs(cents_off) / 5)
    score = int(accuracy * 0.7 + (voiced_pct / 100) * 30)

    feedback = []
    if abs(cents_off) < 25:
        score = min(score + 20, 100)
        feedback.append("✅ Excellent pitch match!")
    elif abs(cents_off) < 50:
        feedback.append("⚠️ Close! You were a bit sharp/flat.")
    else:
        feedback.append(f"❌ You were {abs(cents_off):.0f} cents off. Listen more carefully.")

    return min(score, 100), feedback, {"Pitch Accuracy": accuracy}


def evaluate_major_scale(processor, target_freq):
    """Level 2.1: Major scale ascending evaluation."""
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]

    if len(valid_pitches) < 20:
        return 0, ["❌ Not enough pitch data. Please sing the full scale."], {
            "Pitch Accuracy": 0,
            "Stability": 0,
            "Consistency": 0,
        }

    accuracy = max(0, 100 - np.mean(np.abs(1200 * np.log2(valid_pitches / target_freq))) / 10)
    sagging = processor.measure_pitch_sagging(target_freq)
    stability = processor.analyze_stability() * 100
    breath_consistency = processor.measure_breath_consistency()

    score = int(accuracy * 0.4 + (100 - sagging) * 0.3 + stability * 0.2 + breath_consistency * 0.1)

    feedback = []
    if accuracy > 80:
        feedback.append("✅ Excellent pitch accuracy! Notes are right on target.")
    elif accuracy > 60:
        feedback.append("⚠️ Good pitch, but some notes drifted slightly.")
    else:
        feedback.append("❌ Pitch accuracy needs work. Listen more carefully to each note.")

    if sagging < 20:
        feedback.append("✅ No pitch sagging detected. Great support!")
    elif sagging < 50:
        feedback.append("⚠️ Slight sagging on the higher notes. Maintain breath support.")
    else:
        feedback.append("❌ Significant pitch sagging. Focus on breath control.")

    return min(score, 100), feedback, {
        "Pitch Accuracy": accuracy,
        "No Sagging": 100 - sagging,
        "Stability": stability,
    }


def evaluate_minor_scale(processor, target_freq):
    """Level 2.3: Minor scale evaluation (detect ♭3, ♭6, ♭7)."""
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]

    if len(valid_pitches) < 20:
        return 0, ["❌ Not enough pitch data. Please sing the full scale."], {
            "Scale Accuracy": 0,
        }

    accuracy = max(0, 100 - np.mean(np.abs(1200 * np.log2(valid_pitches / target_freq))) / 10)
    score = int(accuracy * 100)

    feedback = []
    if accuracy > 80:
        feedback.append("✅ Excellent minor scale execution!")
    else:
        feedback.append("⚠️ Some notes were off. Ensure you're hitting ♭3, ♭6, and ♭7.")

    return min(score, 100), feedback, {"Scale Accuracy": accuracy}


def evaluate_intervals(processor, target_freq1, target_freq2):
    """Level 2.4: Interval training evaluation."""
    cents_off = processor.measure_pitch_accuracy(target_freq1)
    voiced_pct = processor.detect_voiced_frames()

    if cents_off is None or voiced_pct < 30:
        return 0, ["❌ Not enough singing detected."], {"Accuracy": 0, "Clarity": 0}

    accuracy = max(0, 100 - abs(cents_off) / 5)
    clarity = min(voiced_pct, 100)
    score = int(accuracy * 0.7 + clarity * 0.3)

    feedback = []
    if abs(cents_off) < 30:
        feedback.append("✅ Excellent interval match!")
    elif abs(cents_off) < 60:
        feedback.append("⚠️ Good interval, but slightly off in pitch.")
    else:
        feedback.append("❌ Interval needs adjustment. Listen to the target again.")

    return min(score, 100), feedback, {"Interval Accuracy": accuracy, "Clarity": clarity}


def evaluate_arpeggios(processor, target_freq):
    """Level 2.5: Arpeggios evaluation (leap accuracy)."""
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]

    if len(valid_pitches) < 15:
        return 0, ["❌ Not enough pitch data. Please sing the full arpeggio."], {
            "Leap Accuracy": 0,
            "Tone": 0,
        }

    accuracy = max(0, 100 - np.mean(np.abs(1200 * np.log2(valid_pitches / target_freq))) / 10)
    register_break = processor.detect_register_break()
    tone_quality = (1.0 - min(processor.analyze_breathiness(), 1.0)) * 100

    score = int(accuracy * 0.5 + (100 - register_break) * 0.3 + tone_quality * 0.2)

    feedback = []
    if register_break < 10:
        feedback.append("✅ Clean leaps! No register breaks detected.")
    else:
        feedback.append("⚠️ Some vocal cracks on the leaps. Focus on smooth transitions.")

    if tone_quality > 80:
        feedback.append("✅ Excellent tone quality throughout.")
    else:
        feedback.append("⚠️ Tone was breathy. Use a more supported vowel.")

    return min(score, 100), feedback, {
        "Leap Accuracy": accuracy,
        "No Cracks": 100 - register_break,
        "Tone": tone_quality,
    }


def evaluate_pitch_stability(processor, target_freq, duration_seconds=6):
    """Level 2.6: Pitch stability (Hold the Note) evaluation."""
    times, pitches = processor.get_pitch_contour()
    valid_pitches = pitches[pitches > 0]

    if len(valid_pitches) < 10:
        return 0, ["❌ Not enough sustained singing. Please hold the note longer."], {
            "Pitch Drift": 0,
            "Volume": 0,
            "In Target": 0,
        }

    pitch_drift = processor.measure_pitch_drift()
    in_target_pct = processor.pitch_within_target_band(target_freq, cents_tolerance=50)
    breath_consistency = processor.measure_breath_consistency()

    drift_score = max(0, 100 - (pitch_drift / 10))
    volume_score = breath_consistency
    target_score = in_target_pct

    score = int(drift_score * 0.3 + volume_score * 0.3 + target_score * 0.4)

    feedback = []
    if in_target_pct > 80:
        feedback.append(f"✅ Excellent! You were in target {in_target_pct:.0f}% of the time.")
    elif in_target_pct > 50:
        feedback.append(f"⚠️ Good effort, but only {in_target_pct:.0f}% in target. Stay more centered.")
    else:
        feedback.append(f"❌ Only {in_target_pct:.0f}% in target. Focus on hitting and holding the pitch.")

    if pitch_drift < 20:
        feedback.append("✅ Excellent pitch stability!")
    elif pitch_drift < 50:
        feedback.append("⚠️ Some pitch wavering detected. Try to lock into the target.")
    else:
        feedback.append("❌ Too much pitch movement. Keep it steady.")

    if breath_consistency > 75:
        feedback.append("✅ Volume is rock solid!")
    else:
        feedback.append("⚠️ Volume fluctuated. Maintain steady breath support.")

    return min(score, 100), feedback, {
        "Pitch Drift": drift_score,
        "Volume Consistency": volume_score,
        "In Target Band": target_score,
    }