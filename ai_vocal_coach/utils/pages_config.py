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
        "exhalation_asset": "assets/examples/0_1_exhalation.wav",
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
            "You'll complete 3 rounds of pitch matching",
            "Each round: listen to the reference tone as many times as you need",
            "Then sing 'ah' to match that exact pitch",
            "Hold the note steadily for 2–3 seconds before stopping",
            "After all 3 rounds you'll see your overall accuracy score",
        ],
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
            "Release slowly on an 'ah' for 4 seconds",
            "Repeat 5-10 times, building awareness of breath",
        ],
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
            "Breathe in low, expanding your stomach with a diaphragmatic breath",
            "Sing do-re-mi-fa-sol-fa-mi-re-do on 'ah', one note per beat, in one breath",
            "Match each pitch to the reference tones you hear",
            "Keep the tone and rhythm steady across the full phrase",
            "Hold the final 'do' until you are out of breath, without forcing the release",
        ],
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
            "Before each part, take a low diaphragmatic breath",
            "Part 1 - Staccato: sing do-re-mi-fa-sol on 'ah', one note per beat, with a quick gentle pulse and a full stop between notes",
            "Keep each staccato note equally clear, in tune, and the same length; short must not become rushed",
            "Part 2 - Legato: sing the same five notes on 'ah' with one continuous, unbroken exhale and no re-attacks",
            "Compare the result: staccato has silence between notes, while legato is one continuous line",
        ],
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
            "Take a full diaphragmatic breath; eight ascending notes use more air than expected",
            "Sing do-re-mi-fa-sol-la-ti-do, one note per beat, at a steady pace",
            "Ration your air and keep the volume even so support remains for 'ti' and the top 'do'",
            "As pitch rises, keep airflow steady without pushing louder or tightening your throat",
            "Attack every pitch directly without scooping, and land the final 'do' as clearly as the first",
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
            "Take a full diaphragmatic breath before starting at the top note",
            "Sing do-ti-la-sol-fa-mi-re-do, one note per beat, starting and ending on 'do'",
            "Keep or slightly increase breath pressure as you descend; sagging is support relaxing, not a pitch problem",
            "Keep your posture, chin, and throat open as they were on the top note",
            "Land the final low 'do' with the same clarity and pitch accuracy as the starting note",
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
            "Take a full diaphragmatic breath before starting",
            "Sing the natural minor scale ascending and descending: la-ti-do-re-mi-fa-sol-la, one note per beat",
            "Notice the close half-steps between ti-do and mi-fa",
            "Keep the minor third and seventh in their natural minor places; do not sharpen them toward major",
            "Keep breath support even and finish by matching the starting 'la' pitch",
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
            "Listen to the two notes: a lower note followed by a higher note",
            "Sing the lower note first, then the higher note in the same order",
            "Hear the target note in your head before the leap, then attack it directly without sliding",
            "Keep breath support continuous through the jump without a reset or gasp",
            "Keep both notes equally clear, centered, and confident",
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
            "Take a full diaphragmatic breath before starting",
            "Sing do-mi-sol-do-sol-mi-do, one note per beat, as a major triad arpeggio",
            "Anticipate the register shift and let the voice lighten toward the high 'do' instead of forcing chest voice",
            "Keep airflow continuous through every leap, with no gasping or reset",
            "Match volume and tone color across the notes, then make the return transition smooth as you descend",
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
            "Take a full diaphragmatic breath before the note starts",
            "Listen to the reference pitch, then match and sustain it on 'ah' for 6-8 seconds",
            "Set the pitch immediately without sliding or searching for it",
            "Keep breath pressure and volume constant; make small corrections as soon as the gauge shows drift",
            "Finish as cleanly as you started, without a pitch or volume sag in the final second",
        ],
        "exemplar_asset": "assets/examples/2_6_pitch_stability.wav",
    },

    # ── Level 3: Articulation, Vowels & Consonants ─────────────────────────
    "15_Exercise_3.1_Pure_Italian_Vowels": {
        "level": 3,
        "category": "Articulation",
        "title": "3.1 Pure Italian Vowels",
        "description": "Sustain each of the five pure vowels A E I O U with consistent tone",
        "order": 17,
        "skills": ["Vowel Purity", "Tone Consistency", "Resonance"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["Level 2"],
        "instructions": [
            "Take a full diaphragmatic breath before each round",
            "Complete five rounds, one per pure Italian vowel: A (ah), E (eh), I (ee), O (oh), U (oo)",
            "Set the mouth shape before the note and keep it still: open A, slightly wide E, forward-tongued I, rounded O, and forward-rounded U",
            "Hold each vowel for 3-4 seconds with steady pitch, volume, and airflow",
            "Watch for diphthong drift; the vowel shape and sound should stay identical at the start, middle, and end",
            "When a reference tone is available, match pitch first, then apply the vowel shape",
        ],
        "exemplar_asset": "assets/examples/3_1_italian_vowels.wav",
    },
    "16_Exercise_3.2_Vowel_Consistency_Ascending": {
        "level": 3,
        "category": "Articulation",
        "title": "3.2 Vowel Consistency on Ascending Scale",
        "description": "Maintain identical vowel quality as pitch rises",
        "order": 18,
        "skills": ["Vowel Modification", "Ascending Intonation", "Consistency"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["3.1"],
        "instructions": [
            "Take a full diaphragmatic breath before starting",
            "Sing do-re-mi-fa-sol on 'ah', one note per beat, carrying support all the way to the top",
            "Fix the jaw, tongue, and lip shape on the first note and do not let it move as pitch rises",
            "Keep breath support constant or increasing so the mouth does not tighten to compensate",
            "Check that the top 'sol' has the same vowel color as the bottom 'do', only higher in pitch",
        ],
        "exemplar_asset": "assets/examples/3_2_vowel_ascending.wav",
    },
    "17_Exercise_3.3_Vowel_Modification_High_Notes": {
        "level": 3,
        "category": "Articulation",
        "title": "3.3 Vowel Modification on High Notes",
        "description": "Open the vowel slightly at the passaggio to keep the tone free",
        "order": 19,
        "skills": ["Passaggio", "Vowel Modification", "Register Transition"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["3.2"],
        "instructions": [
            "Identify your approximate passaggio by noticing where a slow upward slide on 'ah' wants to shift or strain",
            "Starting a few notes below it, sing do-re-mi-fa-sol on 'ah', ending a few notes above the break",
            "As you approach the break, open 'ah' slightly toward 'aw'; make the change subtle and gradual",
            "Keep the tone forward and bright while letting it lighten instead of forcing chest voice upward",
            "Check for a free tone with no strain, sudden flip, or volume drop; adjust the timing or size of the modification if needed",
        ],
        "exemplar_asset": "assets/examples/3_3_vowel_modification.wav",
    },
    "18_Exercise_3.4_Consonant_Clarity": {
        "level": 3,
        "category": "Articulation",
        "title": "3.4 Consonant Clarity",
        "description": "Sing syllable patterns with clear, defined consonant attacks",
        "order": 20,
        "skills": ["Consonant Attack", "Articulation", "Onset Clarity"],
        "difficulty": "Intermediate",
        "duration_minutes": 10,
        "prerequisites": ["3.1"],
        "instructions": [
            "Choose a comfortable single pitch or sing do-re-mi-fa-sol at a steady, moderate tempo",
            "Round 1 - 'Na-Na-Na-Na-Na': tap the tongue tip behind the upper front teeth, then release into 'ah'",
            "Round 2 - 'Ma-Ma-Ma-Ma-Ma': close the lips fully, then release directly into 'ah' without carrying lip tension",
            "Round 3 - 'La-La-La-La-La' and Round 4 - 'Ra-Ra-Ra-Ra-Ra': use a relaxed tongue tap and a light single 'r' flip",
            "Keep every consonant quick and every 'ah' pure, with equal clarity and volume from the first repetition to the fifth",
        ],
        "exemplar_asset": "assets/examples/3_4_consonant_clarity.wav",
    },
    "19_Exercise_3.5_Tongue_Tension": {
        "level": 3,
        "category": "Articulation",
        "title": "3.5 Releasing Tongue Tension",
        "description": "Eliminate tongue and jaw tension that clouds vowel resonance",
        "order": 21,
        "skills": ["Tension Release", "Vowel Resonance", "Jaw Freedom"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["3.1"],
        "instructions": [
            "Take a slow, relaxed diaphragmatic breath, then gently massage your jaw and let it drop open",
            "Rest the tongue tip lightly against the lower front teeth without gripping or pressing",
            "Choose a comfortable pitch and sustain 'ah' for 5 seconds; notice whether the tongue bunches or pulls back",
            "If the tone sounds throaty or swallowed, relax the back of the tongue without changing jaw position or pitch",
            "Repeat on 'ee' and 'oo', allowing their narrower shapes while keeping the tongue and jaw free; compare the tone quality",
        ],
        "exemplar_asset": "assets/examples/3_5_tongue_tension.wav",
    },
    "20_Exercise_3.6_Diction_Challenge": {
        "level": 3,
        "category": "Articulation",
        "title": "3.6 Diction Challenge — Speak to Sing",
        "description": "Carry spoken clarity directly into melodic singing",
        "order": 22,
        "skills": ["Diction", "Text Clarity", "Melodic Speech"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["3.4", "3.5"],
        "instructions": [
            "Phase 1 - Speak: say 'How beautiful upon the mountain' clearly and slightly slower than normal speech",
            "Over-articulate every consonant, especially H, B, T, F, P, M, and N, as if speaking to someone far away",
            "Phase 2 - Sing: sing the same phrase on a five-note descending scale, sol-fa-mi-re-do, at a slow steady tempo",
            "Keep consonants quick and precise while stretching only the vowel to fill each note",
            "Pay special attention to word-ending consonants such as the 'l' in 'beautiful' and the 'n' in 'mountain'; compare speech and singing for equal clarity",
        ],
        "exemplar_asset": "assets/examples/3_6_diction_challenge.wav",
    },

    # ── Level 4: Legato & Musical Line ─────────────────────────────────────
    "21_Exercise_4.1_Connecting_Notes": {
        "level": 4,
        "category": "Legato",
        "title": "4.1 Connecting Notes",
        "description": "Sing three-note slurs with no audible break between pitches",
        "order": 23,
        "skills": ["Legato", "Breath Flow", "Smooth Connection"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["Level 3"],
        "instructions": [
            "Take a full diaphragmatic breath before starting",
            "Sing do-re-mi on 'ah', one note per beat, in one breath",
            "Change pitch without closing the throat or re-attacking; keep the vocal cords and airflow continuously engaged",
            "Keep airflow, vowel, and volume constant across all three notes",
            "Listen for a click, gap, or small re-attack at either transition; slow down and focus on that transition if you hear one",
        ],
        "exemplar_asset": "assets/examples/4_1_connecting_notes.wav",
    },
    "22_Exercise_4.2_Legato_Scales": {
        "level": 4,
        "category": "Legato",
        "title": "4.2 Stepwise Melodies",
        "description": "Sing a 5-note stepwise melody with seamless connection throughout",
        "order": 24,
        "skills": ["Legato Melody", "Phrase Shape", "Breath Arc"],
        "difficulty": "Intermediate",
        "duration_minutes": 15,
        "prerequisites": ["4.1"],
        "instructions": [
            "Take a full diaphragmatic breath before starting and use it evenly across all five notes",
            "Sing do-re-mi-re-do on 'ah', one note per beat, with continuous airflow and no glottal stops",
            "Shape a gentle volume arc: swell slightly toward the peak at 'mi', then recede toward 'do'",
            "Avoid a breath bump or extra push at each pitch change",
            "The phrase should sound like one sustained idea that changes pitch, not five separate attempts",
        ],
        "exemplar_asset": "assets/examples/4_2_stepwise_melodies.wav",
    },
    "23_Exercise_4.3_Phrase_Shaping": {
        "level": 4,
        "category": "Legato",
        "title": "4.3 Breath Phrasing",
        "description": "Place breaths at phrase ends, not mid-phrase",
        "order": 25,
        "skills": ["Phrase Planning", "Breath Economy", "Musical Line"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["4.2"],
        "instructions": [
            "Study the four bars first: bars 1-2 form the first thought and bars 3-4 complete it",
            "Take one full, grounded breath and sing all four bars in one breath if possible; feel the ribs expand rather than lifting the shoulders",
            "If needed, take exactly one breath at the end of bar 2, never in the middle of a bar",
            "Sing the written melody clearly: bar 1 do-re-mi-fa, bar 2 sol-la-sol held, bar 3 fa-mi-re-mi, bar 4 fa-re-do held",
            "If you run out before bar 2 ends, take a fuller breath next time or reduce early volume and breath pressure",
        ],
        "exemplar_asset": "assets/examples/4_3_breath_phrasing.wav",
    },
    "24_Exercise_4.4_Melodic_Etude": {
        "level": 4,
        "category": "Legato",
        "title": "4.4 Melodic Étude",
        "description": "Perform an 8-bar étude with full legato and breath arc",
        "order": 26,
        "skills": ["Musical Line", "Legato", "Phrase Shaping", "Stamina"],
        "difficulty": "Advanced",
        "duration_minutes": 20,
        "prerequisites": ["4.3"],
        "instructions": [
            "Take a full diaphragmatic breath for each four-bar phrase; plan breaths at the end of bars 4 and 8",
            "Sing bars 1-4 on 'ah' in one breath: do-re-mi-fa / sol-la-ti-do / ti-la-sol-fa / mi-re-do held",
            "Breathe at the end of bar 4, then sing bars 5-8 in a second breath: mi-fa-sol-la / ti-do-re-do / ti-la-sol-fa / mi-re-do held",
            "Connect every note with continuous airflow, keep 'ah' identical, and swell gently to each phrase peak at bar 2 or bar 6 before resolving",
            "Match the starting and ending energy; the final bar should not lose volume, support, or pitch accuracy",
        ],
        "exemplar_asset": "assets/examples/4_4_melodic_etude.wav",
    },
    "24b_Exercise_4.5_Simple_Vocalises": {
        "level": 4,
        "category": "Legato",
        "title": "4.5 Simple Vocalises",
        "description": "Apply legato technique to short classical vocalises",
        "order": 27,
        "skills": ["Legato", "Breath Flow", "Phrase Shaping"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["4.4"],
        "instructions": [
            "Choose 'ah' or 'oo' and take one full diaphragmatic breath for the entire vocalise",
            "Sing do-mi-sol-mi-do, one note per beat, holding the final 'do' for two beats",
            "Keep continuous airflow through both leaps, resisting the urge to re-attack each note",
            "Swell slightly toward the peak at 'sol', then ease back down to the closing 'do'",
            "Keep the chosen vowel and pitch clear and consistent from the first note through the fully finished final note",
        ],
    },

    # ── Level 5: Rhythm, Pulse & Musical Timing ────────────────────────────
    "25_Exercise_5.1_Singing_Metronome": {
        "level": 5,
        "category": "Rhythm",
        "title": "5.1 Singing with a Metronome",
        "description": "Place every note exactly on the beat at a steady tempo",
        "order": 27,
        "skills": ["Pulse", "Beat Accuracy", "Steady Tempo"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["Level 4"],
        "instructions": [
            "Listen to the click track — internalize the pulse before singing",
            "Sing quarter notes on 'TA' or 'DA', one per click",
            "Each note must start exactly on the beat — not before, not after",
            "Keep going for 4 bars without stopping",
            "If you drift, reset to the click — don't rush or drag to catch up",
        ],
        "exemplar_asset": "assets/examples/5_1_metronome.wav",
    },
    "26_Exercise_5.2_Quarter_Note_Pulse": {
        "level": 5,
        "category": "Rhythm",
        "title": "5.2 Simple Rhythmic Patterns",
        "description": "Clap and sing quarter- and half-note patterns with precision",
        "order": 28,
        "skills": ["Note Values", "Quarter Notes", "Half Notes"],
        "difficulty": "Intermediate",
        "duration_minutes": 12,
        "prerequisites": ["5.1"],
        "instructions": [
            "Pattern: two quarter notes then one half note (TA TA TAA)",
            "Clap the pattern first, then sing it on one pitch",
            "The half note should last exactly two beats — no cutting it short",
            "Repeat the pattern 4 times in a row at 80 BPM",
            "Keep your body still — let the rhythm live in your breath, not your body",
        ],
        "exemplar_asset": "assets/examples/5_2_simple_rhythms.wav",
    },
    "27_Exercise_5.3_Dotted_Rhythms": {
        "level": 5,
        "category": "Rhythm",
        "title": "5.3 Compound Time (6/8)",
        "description": "Feel the compound pulse — two dotted-quarter beats per bar",
        "order": 29,
        "skills": ["Compound Meter", "6/8 Feel", "Triplet Subdivision"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["5.2"],
        "instructions": [
            "Count '1-and-a 2-and-a' — two main beats with three subdivisions each",
            "Sing 'LA-la-la LA-la-la' in 6/8 — stress the 1 and 4",
            "Feel the lilt — 6/8 has a lilting, wave-like feel, not a march",
            "Keep the subdivisions even — no rushing the 'and-a'",
            "4 bars at 60 dotted-quarter BPM",
        ],
        "exemplar_asset": "assets/examples/5_3_compound_time.wav",
    },
    "28_Exercise_5.4_Triplets": {
        "level": 5,
        "category": "Rhythm",
        "title": "5.4 Clapping & Singing Together",
        "description": "Clap a counter-rhythm while sustaining a melodic line",
        "order": 30,
        "skills": ["Independence", "Poly-rhythm", "Coordination"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["5.2"],
        "instructions": [
            "Clap quarter notes while singing half notes — two claps per sung note",
            "The clapping and singing must stay independent — don't merge them",
            "Start by clapping alone (4 bars), then add singing",
            "Keep the clap rhythm steady even when the melody moves",
            "If one falls apart, isolate it and rebuild",
        ],
        "exemplar_asset": "assets/examples/5_4_clap_sing.wav",
    },
    "29_Exercise_5.5_Syncopation": {
        "level": 5,
        "category": "Rhythm",
        "title": "5.5 Syncopation",
        "description": "Place note attacks between the beats for expressive rhythmic feel",
        "order": 31,
        "skills": ["Syncopation", "Off-beat Placement", "Rhythmic Feel"],
        "difficulty": "Advanced",
        "duration_minutes": 15,
        "prerequisites": ["5.3", "5.4"],
        "instructions": [
            "Pattern: rest on beat 1, attack on the 'and' of 1 (off-beat)",
            "Feel the tension of the note arriving slightly early",
            "Hold the off-beat note across beat 2 — it lasts 1.5 beats",
            "Repeat 4 times at 80 BPM — keep the pulse steady underneath",
            "Tap your foot on every beat while singing the syncopation",
        ],
        "exemplar_asset": "assets/examples/5_5_syncopation.wav",
    },

    # ── Level 6: Resonance & Tone Colour ───────────────────────────────────
    "30_Exercise_6.1_Forward_Placement": {
        "level": 6, "category": "Resonance", "title": "6.1 Forward Placement Awareness",
        "description": "Find a clear, forward vocal resonance", "order": 32,
        "skills": ["Resonance", "Projection", "Tone Colour"], "difficulty": "Intermediate", "duration_minutes": 12,
        "prerequisites": ["Level 5"], "instructions": ["Hum gently, then open to 'ah'", "Feel vibration toward the lips and cheekbones", "Keep the throat relaxed", "Sustain a bright, focused tone", "Repeat at three comfortable pitches"],
    },
    "31_Exercise_6.2_Resonance_Colours": {
        "level": 6, "category": "Resonance", "title": "6.2 Resonance Colours",
        "description": "Explore nasal ring, balanced resonance, and dark tone", "order": 33,
        "skills": ["Resonance", "Tone Colour", "Awareness"], "difficulty": "Intermediate", "duration_minutes": 12,
        "prerequisites": ["6.1"], "instructions": ["Sing one note with a light forward ring", "Repeat with a balanced open tone", "Repeat with a warmer, darker colour", "Keep the sound free rather than forced", "Notice how the resonance changes"],
    },
    "32_Exercise_6.3_Mixing_Registers": {
        "level": 6, "category": "Resonance", "title": "6.3 Mixing Registers",
        "description": "Blend chest and head resonance through the passaggio", "order": 34,
        "skills": ["Register Blend", "Resonance", "Connection"], "difficulty": "Advanced", "duration_minutes": 15,
        "prerequisites": ["6.2"], "instructions": ["Begin on a comfortable middle note", "Glide upward on 'oo'", "Let the tone lighten without breaking", "Return downward with the same connection", "Repeat gently without pushing"],
    },
    "33_Exercise_6.4_Crescendo_Decrescendo": {
        "level": 6, "category": "Resonance", "title": "6.4 Crescendo-Decrescendo Control",
        "description": "Shape volume gradually without losing pitch or tone", "order": 35,
        "skills": ["Dynamics", "Tone Control", "Breath Support"], "difficulty": "Advanced", "duration_minutes": 12,
        "prerequisites": ["6.3"], "instructions": ["Sustain one comfortable pitch", "Grow from soft to medium volume", "Reach a controlled peak", "Return gradually to soft", "Keep pitch and resonance stable"],
    },
    "34_Exercise_6.5_Messa_Di_Voce": {
        "level": 6, "category": "Resonance", "title": "6.5 Messa di Voce",
        "description": "Sustain a note while shaping a complete dynamic arc", "order": 36,
        "skills": ["Dynamic Shaping", "Stability", "Breath Control"], "difficulty": "Advanced", "duration_minutes": 15,
        "prerequisites": ["6.4"], "instructions": ["Start the note softly", "Increase volume smoothly", "Hold the centre of the dynamic arc", "Release back to soft", "Stop before the tone becomes pressed"],
    },

    # ── Level 7: Classical Technique ──────────────────────────────────────
    "35_Exercise_7.1_Portamento": {
        "level": 7, "category": "Classical Technique", "title": "7.1 Portamento Accuracy",
        "description": "Connect wider pitches with a controlled vocal glide", "order": 37,
        "skills": ["Portamento", "Pitch Connection", "Legato"], "difficulty": "Advanced", "duration_minutes": 15,
        "prerequisites": ["Level 6"], "instructions": ["Sing two comfortable target notes", "Glide between them slowly and evenly", "Arrive clearly at the second pitch", "Avoid scooping below the target", "Repeat descending"],
    },
    "36_Exercise_7.2_Register_Turning_Points": {
        "level": 7, "category": "Classical Technique", "title": "7.2 Register Turning Points",
        "description": "Navigate register changes without a crack or squeeze", "order": 38,
        "skills": ["Registers", "Release", "Connection"], "difficulty": "Advanced", "duration_minutes": 15,
        "prerequisites": ["7.1"], "instructions": ["Choose a five-note pattern near your transition", "Sing upward softly", "Allow the resonance to adjust naturally", "Return without dropping the support", "Repeat with a slightly brighter vowel"],
    },
    "37_Exercise_7.3_Ornamentation": {
        "level": 7, "category": "Classical Technique", "title": "7.3 Ornamentation Basics",
        "description": "Add a simple grace note with clarity and control", "order": 39,
        "skills": ["Grace Notes", "Agility", "Pitch Accuracy"], "difficulty": "Advanced", "duration_minutes": 15,
        "prerequisites": ["7.2"], "instructions": ["Sing the main note cleanly", "Add one quick grace note before it", "Keep the main beat stable", "Do not rush the landing pitch", "Repeat in both directions"],
    },
    "38_Exercise_7.4_Slow_Melismas": {
        "level": 7, "category": "Classical Technique", "title": "7.4 Slow Melismatic Lines",
        "description": "Move through several pitches on one vowel with control", "order": 40,
        "skills": ["Melisma", "Legato", "Breath Flow"], "difficulty": "Advanced", "duration_minutes": 18,
        "prerequisites": ["7.3"], "instructions": ["Sing five notes on one vowel", "Keep the vowel stable through each pitch", "Connect every note without a break", "Keep the rhythm even", "Repeat slowly with a relaxed jaw"],
    },
    "39_Exercise_7.5_Fast_Runs": {
        "level": 7, "category": "Classical Technique", "title": "7.5 Fast Runs",
        "description": "Build accuracy and freedom in simple coloratura patterns", "order": 41,
        "skills": ["Agility", "Pitch Accuracy", "Coordination"], "difficulty": "Advanced", "duration_minutes": 18,
        "prerequisites": ["7.4"], "instructions": ["Start the pattern slowly", "Keep each pitch distinct", "Increase speed only while accurate", "Keep the jaw and tongue free", "Finish with a clear landing note"],
    },

    # ── Levels 8-9: Repertoire ─────────────────────────────────────────────
    "40_Exercise_8.1_Caro_Mio_Ben": {
        "level": 8, "category": "Repertoire I", "title": "8.1 Caro mio ben Phrases",
        "description": "Apply technique to short Italian art-song phrases", "order": 42,
        "skills": ["Repertoire", "Italian Diction", "Phrasing"], "difficulty": "Advanced", "duration_minutes": 20,
        "prerequisites": ["Level 7"], "instructions": ["Speak the phrase clearly first", "Sing the short phrase on the text", "Keep the legato line connected", "Plan the breath at the phrase end", "Repeat with expressive but relaxed tone"],
    },
    "41_Exercise_8.2_Amarilli_Mia_Bella": {
        "level": 8, "category": "Repertoire I", "title": "8.2 Amarilli mia bella Exercise",
        "description": "Build phrase shape and diction in an Italian song excerpt", "order": 43,
        "skills": ["Repertoire", "Diction", "Expression"], "difficulty": "Advanced", "duration_minutes": 20,
        "prerequisites": ["8.1"], "instructions": ["Speak the text in rhythm", "Mark the important words", "Sing the excerpt with connected vowels", "Keep consonants light and clear", "Shape the phrase toward its peak"],
    },
    "42_Exercise_8.3_Folk_Song_Settings": {
        "level": 8, "category": "Repertoire I", "title": "8.3 Folk Song Settings",
        "description": "Carry classical technique into a simple folk melody", "order": 44,
        "skills": ["Musicality", "Phrasing", "Tone"], "difficulty": "Intermediate", "duration_minutes": 15,
        "prerequisites": ["8.2"], "instructions": ["Listen for the melody shape", "Sing the tune simply and clearly", "Keep the vowel consistent", "Use a natural expressive dynamic", "Take breaths only at musical commas"],
    },
    "43_Exercise_8.4_Italian_Art_Song": {
        "level": 8, "category": "Repertoire I", "title": "8.4 Italian Art Song Segments",
        "description": "Combine diction, breath, resonance, and legato in short segments", "order": 45,
        "skills": ["Repertoire", "Legato", "Diction", "Expression"], "difficulty": "Advanced", "duration_minutes": 20,
        "prerequisites": ["8.3"], "instructions": ["Speak the segment before singing", "Identify the phrase boundary", "Sing with clear Italian vowels", "Keep the line supported through the final word", "Repeat with a more intentional phrase shape"],
    },
    "44_Exercise_9.1_Italian_Art_Songs": {
        "level": 9, "category": "Repertoire II", "title": "9.1 Complete Italian Art Songs",
        "description": "Perform a complete Italian song with sustained technique", "order": 46,
        "skills": ["Full Performance", "Italian Diction", "Stamina"], "difficulty": "Advanced", "duration_minutes": 30,
        "prerequisites": ["Level 8"], "instructions": ["Review the text and translation", "Mark your planned breaths", "Sing the complete song", "Keep technique consistent across sections", "Review the recording and choose one focus"],
    },
    "45_Exercise_9.2_German_Lieder": {
        "level": 9, "category": "Repertoire II", "title": "9.2 Simple German Lieder",
        "description": "Explore clear German diction within a sustained vocal line", "order": 47,
        "skills": ["German Diction", "Repertoire", "Phrasing"], "difficulty": "Advanced", "duration_minutes": 30,
        "prerequisites": ["9.1"], "instructions": ["Speak the text with clear consonants", "Keep vowels tall and connected", "Sing each phrase with its natural stress", "Avoid tightening on final consonants", "Review diction and line together"],
    },
    "46_Exercise_9.3_English_Art_Songs": {
        "level": 9, "category": "Repertoire II", "title": "9.3 Simple English Art Songs",
        "description": "Balance understandable English text with classical legato", "order": 48,
        "skills": ["English Diction", "Legato", "Expression"], "difficulty": "Advanced", "duration_minutes": 25,
        "prerequisites": ["9.1"], "instructions": ["Speak the text naturally", "Keep stressed words supported", "Connect vowels between consonants", "Keep the melody above the speech", "Perform the complete excerpt"],
    },
    "47_Exercise_9.4_Raga_Vocalise": {
        "level": 9, "category": "Repertoire II", "title": "9.4 Raga-Inspired Vocalise",
        "description": "Explore expressive pitch movement in a cross-cultural vocalise", "order": 49,
        "skills": ["Improvisation", "Pitch Control", "Expression"], "difficulty": "Advanced", "duration_minutes": 25,
        "prerequisites": ["9.2", "9.3"], "instructions": ["Listen to the tonic reference", "Sustain the tonal centre", "Explore the suggested scale slowly", "Use controlled slides between notes", "End by resolving clearly to the tonic"],
    },
}


def get_page_info(page_key):
    """Get metadata for a specific page."""
    return PAGES_MANIFEST.get(page_key, {})


def get_pages_by_level(level):
    """Get all pages for a specific level."""
    return {
        k: v for k, v in PAGES_MANIFEST.items()
        if v.get("level") == level and not v.get("is_dashboard")
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
    for level in range(10):
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
    labels = {
        0: "Diagnostics", 1: "Fundamentals", 2: "Advanced",
        3: "Articulation", 4: "Legato", 5: "Rhythm",
        6: "Resonance", 7: "Classical", 8: "Repertoire I", 9: "Repertoire II",
    }
    return labels.get(level, "")


def format_page_listing():
    """Format all pages for display."""
    pages_by_level = {}
    for level in range(10):
        pages = get_pages_by_level(level)
        pages_by_level[level] = sorted(
            pages.items(),
            key=lambda x: x[1].get("order", 0)
        )
    return pages_by_level
