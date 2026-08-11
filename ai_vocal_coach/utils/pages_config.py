"""
Pages Configuration System

Centralized management of all Streamlit pages:
- Order and hierarchy
- Level grouping
- Metadata (description, difficulty, skills)
- Display formatting
"""

PAGES_MANIFEST = {
    "1_Dashboard": {
        "level": 0,
        "category": "Hub",
        "title": "Dashboard",
        "description": "Track your progress, XP, and voice profile",
        "order": 1,
        "is_dashboard": True,
    },
    # Level 0: Diagnostics
    "2a_Exercise_0.1_Warm_Up": {
        "level": 0,
        "category": "Diagnostics",
        "title": "0.1 Vocal Warm-Up",
        "description": "Assess baseline tone and breath control",
        "order": 2,
        "skills": ["Tone Quality", "Breath Support"],
        "difficulty": "Beginner",
        "duration_minutes": 5,
        "instructions": [
            "Stand or sit comfortably with good posture",
            "Inhale through your mouth for 4 seconds",
            "Keep your shoulders relaxed and still",
            "Release a soft 'sss' sound for 15 seconds",
            "Try to keep your airflow steady and smooth",
        ],
        "exemplar_asset": "assets/examples/0_1_warm_up.wav",
    },
    "2b_Exercise_0.2_Range_Finder": {
        "level": 0,
        "category": "Diagnostics",
        "title": "0.2 Range Finder",
        "description": "Detect voice type and vocal range",
        "order": 3,
        "skills": ["Voice Classification", "Range Detection"],
        "difficulty": "Beginner",
        "duration_minutes": 8,
        "instructions": [
            "Find your comfortable starting pitch (middle of your voice)",
            "Sing 'ah' on that pitch for 2 seconds",
            "Step up by one note and repeat",
            "Continue until you reach your highest comfortable note",
            "Rest, then repeat going down to your lowest note",
        ],
        "exemplar_asset": "assets/examples/0_2_range_finder.wav",
    },
    "2c_Exercise_0.3_Ear_Training": {
        "level": 0,
        "category": "Diagnostics",
        "title": "0.3 Ear Training Baseline",
        "description": "Test pitch-matching accuracy for placement",
        "order": 4,
        "skills": ["Pitch Accuracy", "Ear Training"],
        "difficulty": "Beginner",
        "duration_minutes": 10,
        "instructions": [
            "You'll hear a reference note played",
            "Listen carefully to the pitch",
            "Sing 'ah' matching that exact pitch",
            "Hold it for 2 seconds",
            "Wait for the next note and repeat",
        ],
        "exemplar_asset": "assets/examples/0_3_ear_training.wav",
    },
    # Level 1: Fundamentals
    "3_Exercise_1.1_Diaphragmatic_Support": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.1 Diaphragmatic Support",
        "description": "Master breath control and consistency",
        "order": 5,
        "skills": ["Breath Support", "Stability", "Control"],
        "difficulty": "Beginner",
        "duration_minutes": 8,
        "prerequisites": ["Level 0"],
        "instructions": [
            "Stand comfortably with feet shoulder-width apart",
            "Inhale quietly through your nose for 4 seconds",
            "Feel your lower ribs expand outward (not your chest)",
            "Exhale with a steady 'sss' sound for 15+ seconds",
            "Focus on smooth, consistent airflow",
        ],
        "exemplar_asset": "assets/examples/1_1_diaphragmatic.wav",
    },
    "4_Exercise_1.2_Silent_Breath": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.2 Silent Breath Control",
        "description": "Controlled breathing without phonation",
        "order": 6,
        "skills": ["Breath Control", "Awareness"],
        "difficulty": "Beginner",
        "duration_minutes": 5,
        "prerequisites": ["1.1"],
        "instructions": [
            "Sit comfortably and relax your shoulders",
            "Inhale quietly through your nose for 4 seconds",
            "Hold the breath gently for 2 seconds",
            "Exhale slowly and quietly through your nose for 4 seconds",
            "Repeat 5-10 times, building awareness of breath",
        ],
        "exemplar_asset": "assets/examples/1_2_silent_breath.wav",
    },
    "5_Exercise_1.3_Smooth_Onset": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.3 Smooth Onset",
        "description": "Learn to attack notes without harshness",
        "order": 7,
        "skills": ["Onset Control", "Tone Quality"],
        "difficulty": "Beginner",
        "duration_minutes": 7,
        "prerequisites": ["1.1"],
        "instructions": [
            "Take a comfortable breath using diaphragmatic support",
            "Think of a soft 'ah' sound starting gently",
            "Begin the note smoothly without a hard attack",
            "Sustain for 3-4 seconds with steady airflow",
            "Release gently without tension",
        ],
        "exemplar_asset": "assets/examples/1_3_smooth_onset.wav",
    },
    "6_Exercise_1.4_Legato": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.4 Legato Singing",
        "description": "Connect notes smoothly without gaps",
        "order": 8,
        "skills": ["Legato", "Breath Flow", "Connection"],
        "difficulty": "Intermediate",
        "duration_minutes": 10,
        "prerequisites": ["1.1", "1.3"],
        "instructions": [
            "Prepare with a good breath using diaphragm support",
            "Sing three connected notes: do-re-mi on 'ah'",
            "Focus on smooth connections between notes",
            "Avoid stopping or gasping between notes",
            "Maintain steady airflow throughout all three notes",
        ],
        "exemplar_asset": "assets/examples/1_4_legato.wav",
    },
    "7_Exercise_1.5_Five_Note_Scale": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.5 Five-Note Scale",
        "description": "Scale accuracy and breath consistency",
        "order": 9,
        "skills": ["Pitch Accuracy", "Breath Control", "Scales"],
        "difficulty": "Intermediate",
        "duration_minutes": 10,
        "prerequisites": ["1.4"],
        "instructions": [
            "Breathe in using diaphragmatic support",
            "Sing a five-note scale: do-re-mi-fa-sol on 'ah'",
            "Keep each note clear and distinct",
            "Maintain consistent breath support throughout",
            "Use steady airflow for all five notes",
        ],
        "exemplar_asset": "assets/examples/1_5_five_note_scale.wav",
    },
    "8_Exercise_1.6_Staccato_vs_Legato": {
        "level": 1,
        "category": "Fundamentals",
        "title": "1.6 Staccato vs Legato",
        "description": "Master articulation contrast",
        "order": 10,
        "skills": ["Articulation", "Contrast", "Control"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["1.4", "1.5"],
        "instructions": [
            "Part 1 - Staccato: Sing short, separated 'ah' sounds",
            "Keep each note distinct with brief pauses",
            "Part 2 - Legato: Sing the same notes smoothly connected",
            "Flow the airflow continuously between notes",
            "Feel the contrast between the two styles",
        ],
        "exemplar_asset": "assets/examples/1_6_staccato_legato.wav",
    },
    # Level 2: Advanced
    "9_Exercise_2.1_Major_Scale_Ascending": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.1 Major Scale Ascending",
        "description": "Master ascending major scales at multiple pitches",
        "order": 11,
        "skills": ["Pitch Accuracy", "Scales", "Intonation"],
        "difficulty": "Intermediate",
        "duration_minutes": 15,
        "prerequisites": ["Level 1"],
        "instructions": [
            "Take a full, supported breath",
            "Sing the major scale ascending: do-re-mi-fa-sol-la-ti-do",
            "Focus on clear, distinct pitches at each step",
            "Maintain consistent breath support going up",
            "Keep your tone focused and connected",
        ],
        "exemplar_asset": "assets/examples/2_1_major_ascending.wav",
    },
    "10_Exercise_2.2_Major_Scale_Descending": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.2 Major Scale Descending",
        "description": "Control pitch descent and avoid sagging",
        "order": 12,
        "skills": ["Pitch Control", "Sagging Prevention", "Support"],
        "difficulty": "Intermediate",
        "duration_minutes": 15,
        "prerequisites": ["2.1"],
        "instructions": [
            "Start at the high note (ti) with good breath support",
            "Sing the scale descending: ti-la-sol-fa-mi-re-do",
            "Resist the urge to let notes sag going down",
            "Keep consistent breath pressure throughout",
            "Maintain clear pitch on every note",
        ],
        "exemplar_asset": "assets/examples/2_2_major_descending.wav",
    },
    "11_Exercise_2.3_Minor_Scales": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.3 Minor Scales",
        "description": "Natural minor (♭3, ♭6, ♭7) accuracy",
        "order": 13,
        "skills": ["Scale Degrees", "Pitch Accuracy", "Minor Tonality"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["2.1"],
        "instructions": [
            "Prepare with a full breath",
            "Sing the natural minor scale: la-ti-do-re-mi-fa-sol-la",
            "Listen for the darker tone compared to major",
            "Maintain clear intonation on each step",
            "Keep consistent support and connection",
        ],
        "exemplar_asset": "assets/examples/2_3_minor_scales.wav",
    },
    "12_Exercise_2.4_Intervals": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.4 Interval Training",
        "description": "Leap accuracy between non-adjacent pitches",
        "order": 14,
        "skills": ["Intervals", "Leaps", "Pitch Matching"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["2.1"],
        "instructions": [
            "You'll hear two notes and sing both",
            "First at lower pitch, then at higher pitch",
            "Focus on accurate interval jumps",
            "Maintain steady breath support on the leaps",
            "Keep your tone clear on both pitches",
        ],
        "exemplar_asset": "assets/examples/2_4_intervals.wav",
    },
    "13_Exercise_2.5_Arpeggios": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.5 Arpeggios",
        "description": "Vertical leaps with clarity and tone control",
        "order": 15,
        "skills": ["Leaps", "Register Breaks", "Tone Consistency"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["2.4"],
        "instructions": [
            "Prepare with a supported breath",
            "Sing a major triad arpeggio: do-mi-sol-do",
            "Maintain consistent tone quality across all jumps",
            "Avoid cracks or breaks between the notes",
            "Keep even volume and connection",
        ],
        "exemplar_asset": "assets/examples/2_5_arpeggios.wav",
    },
    "14_Exercise_2.6_Pitch_Stability": {
        "level": 2,
        "category": "Pitch & Scales",
        "title": "2.6 Pitch Stability",
        "description": "Sustain notes with perfect stability",
        "order": 16,
        "skills": ["Pitch Drift Control", "Volume Consistency", "Stamina"],
        "difficulty": "Advanced",
        "duration_minutes": 10,
        "prerequisites": ["2.1"],
        "instructions": [
            "You'll hear a reference pitch",
            "Sustain a matching note for 6-8 seconds",
            "Keep the pitch rock-solid without drifting",
            "Maintain consistent volume throughout",
            "Watch the real-time feedback gauge",
        ],
        "exemplar_asset": "assets/examples/2_6_pitch_stability.wav",
    },
}


def get_page_info(page_key):
    """Get metadata for a specific page."""
    return PAGES_MANIFEST.get(page_key, {})


def get_pages_by_level(level):
    """Get all pages for a specific level."""
    return {
        k: v for k, v in PAGES_MANIFEST.items()
        if v.get("level") == level
    }


def get_pages_by_category(category):
    """Get all pages for a specific category."""
    return {
        k: v for k, v in PAGES_MANIFEST.items()
        if v.get("category") == category
    }


def get_level_progress(completed_exercises):
    """Calculate progress for each level."""
    progress = {}
    for level in [0, 1, 2]:
        pages = get_pages_by_level(level)
        completed = sum(
            1 for k in pages.keys()
            if k in completed_exercises
        )
        progress[level] = {
            "total": len(pages),
            "completed": completed,
            "percentage": int((completed / len(pages) * 100) if pages else 0),
        }
    return progress


def is_page_unlocked(page_key, completed_exercises, voice_profile):
    """Check if a page should be unlocked for the user."""
    page_info = get_page_info(page_key)

    # Dashboard always unlocked
    if page_info.get("is_dashboard"):
        return True

    # Level 0 always unlocked
    if page_info.get("level") == 0:
        return True

    # Level 1+ requires Level 0 completion
    if page_info.get("level") >= 1:
        level_0_pages = get_pages_by_level(0)
        if not all(k in completed_exercises for k in level_0_pages.keys()):
            return False

    # Level 2 requires Level 1 completion (or placement above it)
    if page_info.get("level") == 2:
        placement_level = voice_profile.get("placement_level", 1)
        if placement_level < 2:
            level_1_complete = all(
                k in completed_exercises
                for k in get_pages_by_level(1).keys()
            )
            if not level_1_complete:
                return False

    # Check individual prerequisites
    prerequisites = page_info.get("prerequisites", [])
    for prereq in prerequisites:
        # Handle prerequisite format like "1.1" or "Level 1"
        matching_pages = [
            k for k in PAGES_MANIFEST.keys()
            if prereq.lower() in k.lower()
        ]
        if matching_pages and not all(
            k in completed_exercises for k in matching_pages
        ):
            return False

    return True


def get_sidebar_display_name(page_key):
    """Get the display name for a page in the Streamlit sidebar."""
    page_info = get_page_info(page_key)
    title = page_info.get("title", page_key)

    # Add difficulty indicator
    difficulty = page_info.get("difficulty", "")
    if difficulty:
        return f"{title} ({difficulty})"
    return title


def get_level_badge(level):
    labels = {0: "Diagnostics", 1: "Fundamentals", 2: "Advanced"}
    return labels.get(level, "")


def format_page_listing():
    """Format all pages for display."""
    pages_by_level = {}
    for level in [0, 1, 2]:
        pages = get_pages_by_level(level)
        pages_by_level[level] = sorted(
            pages.items(),
            key=lambda x: x[1].get("order", 0)
        )
    return pages_by_level
