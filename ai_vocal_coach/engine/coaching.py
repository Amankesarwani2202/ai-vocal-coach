"""
Coaching Language & Feedback Generator

Generates encouraging, non-technical feedback for users
"""


def generate_coaching_summary(score, feedback_list, subscores_dict, exercise_type=None, exercise_id=None):
    """Use explicit event valence and live catalog entries for one summary schema."""
    from utils.pages_config import PAGES_MANIFEST
    from utils.exercise_models import get_profile
    profile = get_profile(exercise_id or exercise_type or "0.1")
    current_code = profile["code"]
    summary = {"score": score, "verdict": "Excellent" if score >= 85 else "Good" if score >= 70 else "Keep practising",
               "what_went_well": [], "work_on": [], "observations": [], "next_time": "", "weakest_metrics": []}
    seen = set()
    for event in feedback_list:
        # Old untagged feedback is an observation; never infer praise from wording.
        item = event if isinstance(event, dict) else {"message": str(event), "valence": "neutral"}
        message = item.get("message", "").strip()
        if not message or message.lower() in seen:
            continue
        seen.add(message.lower())
        bucket = {"positive": "what_went_well", "negative": "work_on", "neutral": "observations"}.get(item.get("valence"), "observations")
        summary[bucket].append(message)
    if not summary["what_went_well"]:
        summary["what_went_well"] = ["No clear strength was confirmed in this take yet. Use the measurements and listening notes below."]
    if not summary["work_on"]:
        summary["work_on"] = ["No specific correction was confirmed. Repeat the complete exercise and compare the measured skill."]
    if not subscores_dict:
        summary["next_time"] = "Record this exercise again so the coach has a clear, complete take to measure."
        return summary
    lowest = min(subscores_dict.values())
    weakest = [(name, value) for name, value in subscores_dict.items() if value <= lowest + 3]
    summary["weakest_metrics"] = [name for name, value in weakest]
    actions = {
        "Pitch Accuracy": "Listen to the written pattern and check each note landing slowly.",
        "Pitch Stability": "Settle on the reference early and keep the pitch centred through the hold.",
        "Evenness": "Give each note the same breath energy without extra pushes.",
        "Continuity": "Connect the phrase on one airflow, breathing only at the marked points.",
        "Contrast": "Separate every note in Part 1, then connect the same notes in Part 2.",
        "Glide Smoothness": "Repeat a slow rise and return, keeping the rate of pitch change smooth.",
        "Register Connection": "Let the tone lighten through the transition and listen for abrupt breaks.",
        "Dynamic Control": "Grow gently from soft to a controlled peak, then return gradually to soft.",
        "Sustain": "Take a fuller breath and finish the requested duration without forcing the release.",
        "Vowel Consistency": "Keep each intended vowel's mouth shape the same throughout its round.",
        "Onset Clarity": "Make each consonant quick and defined, then release into the vowel.",
        "Articulation Transfer": "Bring the spoken phrase's consonant definition into the sung phrase.",
        "Tone Colour Contrast": "Use one comfortable pitch and make bright, balanced, and dark rounds clearly different.",
        "Beat Accuracy": "Listen to a few clicks first, then place each attack exactly on its written beat.",
        "Off-beat Placement": "Wait through the first half beat and attack on the 'and' of 1.",
        "Pattern Completion": "Count the complete written pattern and perform every attack once.",
        "Tempo Consistency": "Keep the underlying click steady through every repetition.",
        "Note Values": "Hold each long note for its full written beat value.",
        "Compound Grouping": "Group the six subdivisions as 3+3 and stress the first of each group.",
        "Voice Independence": "Keep quarter-note claps steady while holding the voice for two beats.",
        "Airflow Steadiness": "Keep the exhalation even from the start to the release.",
        "Support Duration": "Use a comfortable full breath and finish the eight-second exhalation.",
        "Voice Presence": "Choose a comfortable pitch and record the full exercise clearly.",
    }
    preferred = {"Pitch Accuracy": ["1.5", "2.1", "2.2"], "Pitch Stability": ["2.6", "1.3"],
                 "Evenness": ["1.1", "1.5"], "Continuity": ["4.1", "1.4"], "Contrast": ["1.4", "4.1"],
                 "Glide Smoothness": ["7.1", "6.3"], "Register Connection": ["6.3", "7.2"],
                 "Dynamic Control": ["6.4", "4.2"], "Sustain": ["2.6", "1.1"],
                 "Vowel Consistency": ["3.1", "3.2"], "Onset Clarity": ["3.4", "1.3"],
                 "Articulation Transfer": ["3.4", "3.6"], "Tone Colour Contrast": ["6.1", "6.2"],
                 "Beat Accuracy": ["5.1", "5.2"], "Off-beat Placement": ["5.1", "5.5"],
                 "Pattern Completion": ["5.1", "5.2"], "Tempo Consistency": ["5.1", "5.2"],
                 "Note Values": ["5.2", "5.1"], "Compound Grouping": ["5.1", "5.3"],
                 "Voice Independence": ["5.2", "5.4"], "Airflow Steadiness": ["1.1", "0.1"],
                 "Support Duration": ["1.1", "0.1"]}
    recommendations = []
    for name, value in weakest:
        candidates = preferred.get(name, [])
        followup = next((info for code in candidates if code != current_code
                         for info in PAGES_MANIFEST.values()
                         if info.get("title", "").split(" ", 1)[0] == code), None)
        sentence = f"{name}: {value}/100. {actions.get(name, 'Repeat the exercise slowly and compare this measurement.')}"
        if followup:
            sentence += f" Recommended follow-up: Exercise {followup['title']}."
        else:
            sentence += " We recommend doing this exercise again."
        recommendations.append(sentence)
    summary["next_time"] = " ".join(recommendations)
    return summary


def simplify_feedback(technical_feedback):
    """
    Convert technical feedback to beginner-friendly language.

    Args:
        technical_feedback: Dict with technical metrics

    Returns:
        List of simplified feedback strings
    """
    simplified = []

    # Pitch accuracy
    if "pitch_accuracy" in technical_feedback:
        accuracy = technical_feedback["pitch_accuracy"]
        if accuracy >= 85:
            simplified.append("✅ Your pitch was right on target!")
        elif accuracy >= 70:
            simplified.append("⚠️ Your pitch was close. Try to match the target note more precisely.")
        else:
            simplified.append("⚠️ Your pitch wandered from the target. Listen carefully to the reference tone.")

    # Pitch stability
    if "pitch_stability" in technical_feedback:
        stability = technical_feedback["pitch_stability"]
        if stability >= 85:
            simplified.append("✅ Your pitch was very steady.")
        elif stability >= 70:
            simplified.append("⚠️ Your pitch wobbled a bit. Try to keep it more stable.")
        else:
            simplified.append("⚠️ Your pitch drifted noticeably. Focus on keeping it steady.")

    # Breath consistency
    if "breath_consistency" in technical_feedback:
        consistency = technical_feedback["breath_consistency"]
        if consistency >= 85:
            simplified.append("✅ Your airflow was very steady.")
        elif consistency >= 70:
            simplified.append("⚠️ Your airflow became less steady towards the end.")
        else:
            simplified.append("⚠️ Your airflow was uneven. Try to maintain steady pressure.")

    # Pitch sagging
    if "pitch_sagging" in technical_feedback:
        sagging = technical_feedback["pitch_sagging"]
        if sagging < 20:
            simplified.append("✅ Great control on the higher notes!")
        elif sagging < 40:
            simplified.append("⚠️ Your notes dipped slightly on the higher parts. Maintain your breath support.")
        else:
            simplified.append("⚠️ Your notes sagged on the higher parts. Focus on breath support.")

    # Register breaks
    if "register_breaks" in technical_feedback:
        breaks = technical_feedback["register_breaks"]
        if breaks == 0:
            simplified.append("✅ No cracks or breaks detected!")
        elif breaks <= 2:
            simplified.append("⚠️ A slight crack detected. Keep your voice smooth and connected.")
        else:
            simplified.append("⚠️ Multiple cracks detected. Focus on smooth transitions between notes.")

    # Sustain duration
    if "sustain_duration" in technical_feedback:
        duration = technical_feedback["sustain_duration"]
        if duration >= 15:
            simplified.append("✅ Excellent breath stamina!")
        elif duration >= 10:
            simplified.append("⚠️ Your breath ran out a bit early. Try to sustain longer with better support.")
        else:
            simplified.append("⚠️ You ran out of breath quickly. Work on building your breath capacity.")

    # Noise/breathiness
    if "breathiness" in technical_feedback:
        breathiness = technical_feedback["breathiness"]
        if breathiness < 30:
            simplified.append("✅ Your voice was clear and focused!")
        elif breathiness < 50:
            simplified.append("⚠️ A little breathy. Try to engage your voice more.")
        else:
            simplified.append("⚠️ Your sound was quite breathy. Focus on creating a more connected sound.")

    return simplified if simplified else ["Keep practicing! Each attempt builds muscle memory."]


def format_timestamped_feedback(feedback_events):
    """
    Format feedback events with timestamps.

    Args:
        feedback_events: List of dicts with time and message

    Returns:
        Formatted feedback list
    """
    formatted = []

    for event in feedback_events:
        time_seconds = event.get("time", 0)
        if isinstance(time_seconds, str) and ":" in time_seconds:
            time_str = time_seconds
        else:
            minutes = int(float(time_seconds) // 60)
            seconds = float(time_seconds) % 60
            time_str = f"{minutes}:{seconds:04.1f}"

        message = event.get("message", "")
        formatted.append({"time": time_str, "message": message})

    return formatted


def generate_encouragement(score, attempt_number=1):
    """
    Generate encouragement message based on performance.

    Args:
        score: Overall score
        attempt_number: Which attempt this is

    Returns:
        Encouraging message string
    """
    if score >= 90:
        return "Outstanding! You're really getting it! 🌟"
    elif score >= 80:
        return "Excellent work! You're building great habits! 💪"
    elif score >= 70:
        return "Good progress! You're learning fast! 🚀"
    elif score >= 60:
        if attempt_number == 1:
            return "Great first attempt! Each try makes you better. 📈"
        else:
            return "Keep going! Consistency is key to improvement. 💪"
    else:
        return "Every expert started as a beginner. You've got this! 🎯"
