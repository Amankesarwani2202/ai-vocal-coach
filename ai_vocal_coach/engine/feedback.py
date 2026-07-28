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