"""
Coaching Language & Feedback Generator

Generates encouraging, non-technical feedback for users
"""


def generate_coaching_summary(score, feedback_list, subscores_dict):
    """
    Generate an encouraging coaching summary.

    Args:
        score: Overall score (0-100)
        feedback_list: List of feedback strings
        subscores_dict: Dictionary of component scores

    Returns:
        Dict with what_went_well, work_on, next_time
    """
    summary = {"what_went_well": [], "work_on": [], "next_time": ""}

    # Normalize feedback_list: accept list of strings or list of dicts
    flat_feedback = []
    for f in feedback_list:
        if isinstance(f, dict):
            flat_feedback.append(f.get("message", ""))
        else:
            flat_feedback.append(str(f))

    import re

    def _matches(text, keywords):
        """Word-boundary safe match — avoids 'try' matching inside 'entry'."""
        t = text.lower()
        for kw in keywords:
            if " " in kw:
                if kw in t:
                    return True
            else:
                if re.search(r'\b' + re.escape(kw) + r'\b', t):
                    return True
        return False

    POSITIVE_KW = ["good", "strong", "excellent", "great", "consistent", "clean", "steady", "solid", "well", "clear", "smooth"]
    NEGATIVE_KW = ["less stable", "less steady", "wobble", "wobbled", "uneven", "improve", "strained", "flat", "sharp", "breathy", "crack", "break", "drift", "thin", "gap", "noisy"]

    # A message is positive if it has positive keywords and NO negative keywords
    positive_feedback = [
        f for f in flat_feedback
        if _matches(f, POSITIVE_KW) and not _matches(f, NEGATIVE_KW)
    ]
    # A message is a concern if it has negative keywords
    areas_to_improve = [
        f for f in flat_feedback
        if _matches(f, NEGATIVE_KW)
    ]

    # What went well
    for feedback in positive_feedback:
        summary["what_went_well"].append(feedback.strip())

    if not summary["what_went_well"]:
        if score >= 85:
            summary["what_went_well"].append("Solid performance overall.")
        elif score >= 70:
            summary["what_went_well"].append("You're on the right track.")

    # Areas to work on
    for feedback in areas_to_improve:
        summary["work_on"].append(feedback.strip())

    if not summary["work_on"]:
        for component, sub_score in subscores_dict.items():
            if sub_score < 70:
                summary["work_on"].append(f"Focus on {component.lower()}.")

    # Next time guidance
    if score >= 85:
        summary["next_time"] = "You're mastering this! Try to maintain this consistency, then push for even higher scores."
    elif score >= 70:
        summary["next_time"] = "Good progress! Work on the areas above, then try again. You'll see improvement with practice."
    else:
        summary["next_time"] = "Don't worry—even professionals started here. Focus on one thing at a time, then try again."

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
        minutes = int(time_seconds // 60)
        seconds = int(time_seconds % 60)
        time_str = f"{minutes:02d}:{seconds:02d}"

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
