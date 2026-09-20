"""
Feedback copy for each error type, keyed by error_id.

Each entry has:
  - primary: the exact copy from the spec
  - variants: 2-4 alternative phrasings (never identical to primary)
  - positive: if True, this is good-news feedback (not an error)

The display layer picks one at random per timestamp to avoid
repeating identical copy within the same result screen.
"""

import random

FEEDBACK = {
    # ── Level 1: 1.5 Five-Note Scale ─────────────────────────────────────
    "L1_RUSHING_TEMPO": {
        "primary": "You're moving faster than the beat — slow down and give each note its full length.",
        "variants": [
            "That note was rushed — try to match the steady beat on every one.",
            "Give each note equal time; you sped up here.",
            "Rushing through the notes — keep a steady, even pace.",
        ],
    },
    "L1_BREATH_DROPOUT": {
        "primary": "Your breath ran low near the top — try a fuller breath before you start.",
        "variants": [
            "The last note lost power — take a deeper breath at the beginning.",
            "Breath support faded by the end — fill up more before starting.",
            "You ran out of air on the final note — breathe a little deeper.",
        ],
    },
    "L1_PITCH_FLAT_LATER": {
        "primary": "Pitch drifted flat as you went up — keep breath support steady, not just at the start.",
        "variants": [
            "The higher notes went flat — maintain steady support all the way up.",
            "Your pitch sagged on the later notes — even breath pressure helps.",
            "Notes toward the top drifted flat — keep your air moving consistently.",
        ],
    },
    "L1_UNEVEN_VOLUME": {
        "primary": "Some notes were louder than others — aim for the same volume on all five.",
        "variants": [
            "Volume wasn't even across the scale — try to balance all five notes.",
            "A few notes stuck out louder — smooth the volume across the whole set.",
            "Keep the same energy on every note; some were noticeably softer.",
        ],
    },
    "L1_AUDIBLE_GASP": {
        "primary": "Try a silent breath — no audible gasp before you start singing.",
        "variants": [
            "There was a noisy breath before your first note — aim for a quiet intake.",
            "The inhalation was audible — try breathing silently before starting.",
            "Start cleaner by taking a relaxed, silent breath.",
        ],
    },

    # ── Level 1: 1.6 Staccato vs Legato ──────────────────────────────────
    "L1_STACCATO_NOT_SEPARATED": {
        "primary": "Your staccato notes are running together — leave a clear silent gap between each one.",
        "variants": [
            "Those staccato notes need more space — make each one its own short burst.",
            "Separate the staccato notes more clearly with silence between them.",
            "The notes are blending — staccato means a definite gap between each.",
        ],
    },
    "L1_LEGATO_BREAKS": {
        "primary": "There's a small break between notes in your legato — keep the airflow continuous.",
        "variants": [
            "The legato had a gap — the sound should never stop between notes.",
            "Keep the air flowing without interruption through the legato section.",
            "Your legato had brief silences — connect each note smoothly to the next.",
        ],
    },
    "L1_STACCATO_TOO_LONG": {
        "primary": "Make your staccato notes shorter and more separated.",
        "variants": [
            "Those staccato notes are too long — make them quicker and more detached.",
            "Shorten the staccato notes — they should be brief and bouncy.",
        ],
    },
    "L1_STACCATO_PITCH_INACCURATE": {
        "primary": "Some staccato notes aren't landing on pitch — attack each note directly.",
        "variants": [
            "Pitch was off on a staccato note — aim straight for the center of the note.",
            "Hit each staccato note cleanly on pitch, even though they're short.",
        ],
    },
    "L1_NO_CONTRAST": {
        "primary": "Staccato and legato sound too similar — exaggerate the contrast more.",
        "variants": [
            "There should be a clear difference between the two sections — make staccato bouncier and legato smoother.",
            "Push the contrast further — the two parts should feel obviously different.",
        ],
    },

    # ── Level 2: 2.1 Major Scale Ascending ────────────────────────────────
    "L2_PITCH_FLAT_TOP": {
        "primary": "The top notes went flat — take a bigger breath so you have support left for 'ti' and 'do'.",
        "variants": [
            "Pitch dropped on the highest notes — save enough air for the top of the scale.",
            "Your final notes went flat — more breath support is needed at the top.",
            "The scale went flat near the top — keep your support steady all the way up.",
        ],
    },
    "L2_PUSHING_HIGH": {
        "primary": "You're pushing on the high notes — let airflow do the work instead of extra volume.",
        "variants": [
            "The high notes got forced — ease off the volume and let the air carry the pitch.",
            "Don't push harder for higher notes — let your breath, not your throat, do the lifting.",
        ],
    },
    "L2_UNEVEN_TEMPO": {
        "primary": "Your pace wasn't even — try to keep each note the same length.",
        "variants": [
            "Some notes were longer than others — aim for a steady, even rhythm.",
            "The tempo was uneven — give each note the same amount of time.",
        ],
    },
    "L2_SCOOPING": {
        "primary": "You're sliding up into notes — try to land directly on pitch.",
        "variants": [
            "There's a scoop at the start of that note — aim straight for the target pitch.",
            "Land on the pitch cleanly instead of sliding up to it.",
            "Skip the slide — attack the note directly from the start.",
        ],
    },
    "L2_MID_SCALE_BREATH": {
        "primary": "You took an extra breath partway through — try the full scale in one breath.",
        "variants": [
            "There was an unplanned breath mid-scale — aim to get through in one go.",
            "The phrase was interrupted by a breath — try filling up more at the start.",
        ],
    },

    # ── Level 2: 2.2 Major Scale Descending ───────────────────────────────
    "L2_PITCH_SAG_DESCENDING": {
        "primary": "Notes are sagging flat going down — keep your breath pressure up, don't ease off.",
        "variants": [
            "Pitch dropped as you descended — maintain support even on lower notes.",
            "The descending notes went flat — don't let up on your breath support going down.",
        ],
    },
    "L2_VOLUME_FADE_BOTTOM": {
        "primary": "Volume dropped near the end — maintain the same breath energy all the way down.",
        "variants": [
            "The lower notes faded in volume — keep even breath pressure through the descent.",
            "Your volume trailed off — the last note should be as strong as the first.",
        ],
    },
    "L2_START_UNSUPPORTED": {
        "primary": "The very first note was already unstable — take a full breath before starting at the top.",
        "variants": [
            "Your opening note was shaky — make sure you're fully supported before you begin.",
            "Start strong — take a deep breath so the first note is solid.",
        ],
    },
    "L2_TONE_DARKENS": {
        "primary": "Your tone got duller on the way down — keep your posture and throat open, not just your breath.",
        "variants": [
            "The lower notes lost brightness — keep the same open resonance all the way down.",
            "Tone darkened near the bottom — maintain your vocal placement as you descend.",
        ],
    },
    "L2_FINAL_LESS_ACCURATE": {
        "primary": "The ending 'do' wasn't as clean as the starting note — that's a sign of sagging support.",
        "variants": [
            "Your last note was less accurate than the first — keep support consistent throughout.",
            "Compare your first and last notes — the ending should be just as clean.",
        ],
    },

    # ── Level 2: 2.3 Minor Scales ─────────────────────────────────────────
    "L2_MAJORIZING": {
        "primary": "You're pulling toward major — that note should stay natural minor, not sharpened.",
        "variants": [
            "That note sounded major instead of minor — keep it natural, don't sharpen it.",
            "You're majorizing — listen for the minor quality and keep that note lower.",
        ],
    },
    "L2_HALFSTEP_WIDE": {
        "primary": "That half-step is too wide — it should feel tighter than the other intervals.",
        "variants": [
            "The half-step interval is stretched too far — bring it in closer.",
            "Tighten up that half-step — it's wider than it should be.",
        ],
    },
    "L2_KEY_CENTER_DRIFT": {
        "primary": "You drifted from the starting pitch — the final note should match where you began.",
        "variants": [
            "Your ending note doesn't match your starting pitch — you drifted off-center.",
            "The key center shifted — finish on the same pitch you started on.",
        ],
    },
    "L2_SUPPORT_DROPS": {
        "primary": "Support dropped in the second half — pace your breath across the whole scale.",
        "variants": [
            "The back half of the scale lost energy — distribute your breath more evenly.",
            "Support faded in the second half — save enough air for the full scale.",
        ],
    },

    # ── Level 2: 2.4 Interval Training ────────────────────────────────────
    "L2_LEAP_OVERSHOOT": {
        "primary": "The leap missed the target pitch — you went {direction} on the higher note.",
        "variants": [
            "You overshot (or undershot) the interval — land more precisely on the second note.",
            "The second note was off — aim right at the target pitch on the leap.",
        ],
    },
    "L2_SLIDING_LEAP": {
        "primary": "You slid into that note — try to attack the higher pitch directly.",
        "variants": [
            "There was a glide between the notes — jump cleanly to the second pitch.",
            "Skip the slide — go straight to the target note.",
        ],
    },
    "L2_BREATH_CATCH": {
        "primary": "There's a breath catch right at the leap — keep the air flowing through the jump.",
        "variants": [
            "Don't let the air stop at the leap — keep it flowing through the interval.",
            "The breath caught between notes — maintain continuous airflow across the jump.",
        ],
    },
    "L2_SECOND_NOTE_WEAKER": {
        "primary": "Your second note was weaker than the first — keep equal energy on both pitches.",
        "variants": [
            "The higher note lost energy — give it the same support as the first.",
            "Both notes should have equal strength — the second one faded.",
        ],
    },

    # ── Level 2: 2.5 Arpeggios ────────────────────────────────────────────
    "L2_VOCAL_CRACK": {
        "primary": "There's a break in your voice on that jump — ease into the higher note rather than forcing it up.",
        "variants": [
            "Your voice cracked at the register change — lighten up as you approach the top.",
            "There was a vocal break — try easing into the high note with less effort.",
        ],
    },
    "L2_CHEST_TOO_HIGH": {
        "primary": "You're carrying too much weight into the high note — let your voice lighten as you go up.",
        "variants": [
            "The upper note sounds heavy — allow a lighter vocal quality for higher pitches.",
            "Let the voice thin out naturally on the way up instead of pushing chest voice higher.",
        ],
    },
    "L2_TONE_COLOR_CHANGES": {
        "primary": "The three notes don't match in tone — try to keep the same vocal color throughout.",
        "variants": [
            "Tone color shifted across the arpeggio — aim for a consistent sound on every note.",
            "Keep the same brightness and warmth across all the notes.",
        ],
    },
    "L2_UNEVEN_VOLUME_LEAPS": {
        "primary": "Some notes are louder than others — even out the volume across the arpeggio.",
        "variants": [
            "Volume jumped around between notes — smooth it out across the whole arpeggio.",
            "Balance the volume so every note in the arpeggio has the same energy.",
        ],
    },

    # ── Level 2: 2.6 Pitch Stability ──────────────────────────────────────
    "L2_PITCH_DRIFT_FLAT": {
        "primary": "Your pitch drifted flat as the breath ran out — keep support constant through the whole note.",
        "variants": [
            "Pitch sagged flat over the hold — maintain steady breath pressure the entire time.",
            "The note drifted flat — don't let your support ease off as you sustain.",
        ],
    },
    "L2_PITCH_WAVER": {
        "primary": "Pitch is wobbling rather than settling — try to lock onto the note early and hold steady.",
        "variants": [
            "The pitch wavered throughout — focus on locking in and staying centered.",
            "There was too much wobble — aim for a still, centered sustain.",
        ],
    },
    "L2_VOLUME_DECREASE": {
        "primary": "Volume faded as you held the note — keep breath pressure even to the end.",
        "variants": [
            "The note got quieter over time — maintain the same energy throughout the hold.",
            "Volume dropped during the sustain — keep your breath steady.",
        ],
    },
    "L2_SHORT_DURATION": {
        "primary": "You ran out of air before the full hold — take a fuller breath at the start.",
        "variants": [
            "The note ended too soon — breathe deeper before beginning the sustain.",
            "Try to hold for the full duration — a bigger breath at the start helps.",
        ],
    },
    "L2_SLOW_ONSET": {
        "primary": "You're taking too long to settle on pitch — try to land on the note right away.",
        "variants": [
            "The pitch took a while to stabilize — aim to be on pitch from the very start.",
            "Settle onto the note faster — the beginning should be as clean as the middle.",
        ],
    },

    # ── Level 3: 3.1 Pure Italian Vowels ──────────────────────────────────
    "L3_VOWEL_DIPHTHONG": {
        "primary": "The vowel changed partway through — it should sound identical at the start, middle, and end.",
        "variants": [
            "Your vowel shifted during the sustain — lock the shape and hold it still.",
            "That turned into a diphthong — keep the vowel pure from start to finish.",
            "The vowel drifted — maintain the same mouth shape throughout.",
        ],
    },
    "L3_WRONG_VOWEL_COLOR": {
        "primary": "That's not quite a pure {vowel} — check the mouth shape before you start.",
        "variants": [
            "The vowel color was off — review the target mouth position for {vowel}.",
            "Set your mouth shape for a pure {vowel} before you begin sustaining.",
        ],
    },
    "L3_MOUTH_SHIFT": {
        "primary": "Your mouth position moved during the note — lock the shape in place before sustaining.",
        "variants": [
            "The spectral shape changed mid-note — keep your mouth still once you start.",
            "Something shifted in your resonance — hold your mouth position steady.",
        ],
    },
    "L3_DURATION_INCONSISTENT": {
        "primary": "Some vowels were held longer than others — aim for the same length each time.",
        "variants": [
            "The durations varied across rounds — try to hold each vowel for the same amount of time.",
            "Keep the sustain even — all five vowels should be the same length.",
        ],
    },

    # ── Level 3: 3.2 Vowel Consistency on Ascending Scale ─────────────────
    "L3_VOWEL_COLLAPSE": {
        "primary": "The vowel is collapsing toward 'uh' as you go up — keep the same mouth shape all the way to the top.",
        "variants": [
            "Your vowel neutralized on the higher notes — maintain the same shape as you ascend.",
            "The vowel collapsed — don't let higher pitches pull your mouth into a neutral position.",
        ],
    },
    "L3_JAW_TIGHTENS": {
        "primary": "Your jaw is tensing on the higher notes — stay open and relaxed as pitch rises.",
        "variants": [
            "Jaw tension increased on the way up — keep it loose and relaxed.",
            "The higher notes showed signs of jaw tightening — let it stay dropped.",
        ],
    },
    "L3_FIRST_LAST_MISMATCH": {
        "primary": "Compare your first and last note — the top note should sound like the same vowel, just higher.",
        "variants": [
            "The vowel at the top doesn't match the bottom — they should be the same vowel at different pitches.",
            "Your first and last notes had different vowel colors — aim for consistency.",
        ],
    },
    "L3_SUPPORT_DROPS_TOP": {
        "primary": "Support dropped near the top, which is likely pulling your vowel out of shape — keep breath steady.",
        "variants": [
            "Breath support faded at the top of the scale — this affects both pitch and vowel quality.",
            "The upper notes lost support — keep even breath pressure through the whole scale.",
        ],
    },

    # ── Level 3: 3.3 Vowel Modification on High Notes ────────────────────
    "L3_NO_MODIFICATION": {
        "primary": "You're not modifying through the break — try letting the vowel open slightly as you approach it.",
        "variants": [
            "No vowel shift was detected at the passaggio — a slight opening helps you through the break.",
            "Try modifying the vowel as you cross the break — it reduces strain.",
        ],
    },
    "L3_OVER_MODIFICATION": {
        "primary": "That's too much of a shift — the vowel should still sound recognizable, just slightly opened.",
        "variants": [
            "The modification was overdone — keep it subtle, not a different vowel entirely.",
            "Scale back the vowel change — you went too far from the original.",
        ],
    },
    "L3_MODIFICATION_MISTIMED": {
        "primary": "Try shifting the vowel a little {direction} — right now it's not lined up with your break point.",
        "variants": [
            "The modification came at the wrong moment — adjust the timing to match your passaggio.",
            "Align the vowel shift with your actual break point — it's slightly off.",
        ],
    },
    "L3_CRACK_DESPITE_MOD": {
        "primary": "There's still a noticeable break — the modification may need to be slightly larger.",
        "variants": [
            "The break is still audible — try a bit more vowel modification at that point.",
            "You're modifying, but the crack is still there — increase the shift slightly.",
        ],
    },

    # ── Level 3: 3.4 Consonant Clarity ────────────────────────────────────
    "L3_BLURRY_CONSONANT": {
        "primary": "Your consonants are blurring into the vowel — make the attack quicker and more defined.",
        "variants": [
            "The consonant onset was too slow — snap into it faster.",
            "Make the consonant crisper — it's blending into the vowel.",
            "Sharpen the attack — the consonant should be quick and clear.",
        ],
    },
    "L3_CLARITY_FADES": {
        "primary": "The later repetitions got softer — keep the same energy on every repetition.",
        "variants": [
            "Clarity dropped on later reps — maintain the same crispness throughout.",
            "Don't let the consonants fade — the last one should be as clear as the first.",
        ],
    },
    "L3_VOWEL_SHIFTS_ROUNDS": {
        "primary": "Your 'ah' vowel is shifting between rounds — keep it identical regardless of the consonant.",
        "variants": [
            "The vowel changed across different consonant rounds — it should stay the same.",
            "Keep the vowel consistent — only the consonant changes between rounds.",
        ],
    },
    "L3_R_OVER_ARTICULATED": {
        "primary": "That R is heavier than it needs to be — go for a light, quick tap instead.",
        "variants": [
            "The R is over-articulated — make it lighter and faster.",
            "Try a quicker, lighter R — you're spending too much effort on it.",
        ],
    },

    # ── Level 3: 3.5 Releasing Tongue Tension ─────────────────────────────
    "L3_THROATY_TONE": {
        "primary": "The tone sounds throaty — try releasing tension at the back of your tongue.",
        "variants": [
            "There's a swallowed quality to the sound — relax the tongue root.",
            "Your tone is constricted — let the back of the tongue drop and open up.",
        ],
    },
    "L3_JAW_TENSION": {
        "primary": "There's tension in your jaw — let it stay loose and open.",
        "variants": [
            "Your jaw seems tight — relax it and let it hang naturally.",
            "Jaw tension detected — try gently dropping your jaw before sustaining.",
        ],
    },
    "L3_TENSION_VARIES": {
        "primary": "Your 'ee' and 'oo' sound tighter than your 'ah' — those vowels are holding more tension.",
        "variants": [
            "Tension increased on certain vowels — try to keep the same relaxed feeling on all three.",
            "Some vowels were tighter than others — carry the openness of 'ah' into 'ee' and 'oo'.",
        ],
    },
    "L3_STRAIN_PITCH": {
        "primary": "That pitch may be a stretch for you — try a more comfortable note so tension isn't coming from strain.",
        "variants": [
            "The pitch might be too high (or low) for a relaxation exercise — try something more in your comfort zone.",
            "Choose a more comfortable pitch — this exercise is about releasing tension, not range.",
        ],
    },

    # ── Level 3: 3.6 Diction Challenge ────────────────────────────────────
    "L3_CONSONANTS_SOFTEN_SUNG": {
        "primary": "Your consonants were much clearer when spoken — bring that same crispness into the sung version.",
        "variants": [
            "The sung consonants softened compared to spoken — keep the same definition when you sing.",
            "Consonants got mushier when singing — sing with the same articulation you speak with.",
        ],
    },
    "L3_ENDING_CONSONANTS_DROPPED": {
        "primary": "You're dropping the ending consonants — finish the word before releasing the note.",
        "variants": [
            "Word-ending consonants are missing — make sure you complete each word.",
            "Don't skip the final consonant — it needs to sound before the next note starts.",
        ],
    },
    "L3_VOWEL_CROWDS_CONSONANT": {
        "primary": "You're spending too much time on the vowel — leave room to fully finish the consonant before the next note.",
        "variants": [
            "The vowel is taking over the note — reserve time for the consonant at the end.",
            "Balance the note between vowel and consonant — right now the consonant is squeezed out.",
        ],
    },
    "L3_SUNG_DICTION_SOFTER": {
        "primary": "Overall, your sung diction is softer than your spoken diction — try over-articulating like you did in Phase 1.",
        "variants": [
            "Your singing is less clear than your speaking — exaggerate the consonants when you sing.",
            "Bring the spoken clarity into your singing — pretend you're speaking the words on pitch.",
        ],
    },

    # ── Level 4: 4.1 Connecting Notes ─────────────────────────────────────
    "L4_GLOTTAL_STOP": {
        "primary": "There's a small catch between notes — try changing pitch without closing your throat.",
        "variants": [
            "You're stopping the sound between notes — keep the throat open through the pitch change.",
            "There's a glottal stop at the transition — let the air flow continuously.",
        ],
    },
    "L4_BREATH_PULSE": {
        "primary": "You're pushing extra air at each note change — keep the airflow level and let only pitch move.",
        "variants": [
            "There's a breath pulse at each transition — smooth out the air pressure.",
            "The airflow surges at each note — keep it steady and only change the pitch.",
        ],
    },
    "L4_VOWEL_VOLUME_CHANGE": {
        "primary": "Keep the vowel and volume the same across all three notes — only pitch should change.",
        "variants": [
            "Volume shifted between notes — aim for the same energy level on each one.",
            "Only the pitch should be different between notes — keep everything else constant.",
        ],
    },
    "L4_MID_PHRASE_BREATH": {
        "primary": "Try to get through all three notes in one breath.",
        "variants": [
            "There was a breath between notes — this phrase should be one continuous flow.",
            "Keep the air going — all three notes belong in a single breath.",
        ],
    },

    # ── Level 4: 4.2 Stepwise Melodies ────────────────────────────────────
    "L4_BUMPS_AT_CHANGE": {
        "primary": "There are small bumps at each note change — smooth out the breath pressure.",
        "variants": [
            "The volume jumps at each transition — keep the air pressure steady.",
            "Smooth the bumps — the volume shouldn't spike at every pitch change.",
        ],
    },
    "L4_NO_DYNAMIC_ARC": {
        "primary": "Try shaping the phrase — a gentle swell toward the middle note, then easing back down.",
        "variants": [
            "The phrase was flat dynamically — add a subtle rise and fall.",
            "Shape the volume: grow toward the peak and taper back down.",
        ],
    },
    "L4_ARC_OVERDONE": {
        "primary": "That shape is too dramatic — make the swell more subtle.",
        "variants": [
            "The dynamic arc was overdone — dial it back to something gentler.",
            "Ease up on the swell — it should be noticeable but not exaggerated.",
        ],
    },
    "L4_GLOTTAL_STOP_TRANSITION": {
        "primary": "There's a break between notes — keep the connection smooth like in Connecting Notes.",
        "variants": [
            "The legato broke at a transition — keep the sound continuous.",
            "Don't let the throat close between notes — maintain the connection.",
        ],
    },

    # ── Level 4: 4.3 Breath Phrasing ─────────────────────────────────────
    "L4_BREATH_MID_BAR": {
        "primary": "You breathed mid-phrase — try to hold until the end of bar 2.",
        "variants": [
            "The breath was mid-bar — save it for the planned breath point.",
            "Hold the phrase longer — the breath should come at the end of bar 2, not before.",
        ],
    },
    "L4_RAN_OUT_BEFORE_BAR2": {
        "primary": "You were low on air before the natural break — take a fuller breath at the start.",
        "variants": [
            "Breath ran out before bar 2 — fill up more deeply before you begin.",
            "You needed more air — take a bigger breath so you can reach the planned break point.",
        ],
    },
    "L4_STRAINED_THROUGH": {
        "primary": "You made it through, but sounded strained near the end — it's okay to take the planned breath instead of pushing.",
        "variants": [
            "The end sounded forced — use the planned breath point rather than pushing through.",
            "Don't strain to avoid breathing — the planned breath is there for a reason.",
        ],
    },
    "L4_CLEAN_SINGLE_BREATH": {
        "primary": "Nicely done — you sustained the full phrase in one breath.",
        "positive": True,
        "variants": [
            "Great breath management — you held through the whole phrase cleanly.",
            "Excellent — one smooth, supported breath through the entire passage.",
        ],
    },

    # ── Level 4: 4.4 Melodic Étude ────────────────────────────────────────
    "L4_BREATH_WRONG_POINT": {
        "primary": "Your breath landed mid-phrase — the planned points are the ends of bar 4 and bar 8.",
        "variants": [
            "The breath was at the wrong spot — aim for bar 4 and bar 8.",
            "Breathe at the phrase boundaries, not in the middle.",
        ],
    },
    "L4_ENERGY_TRAILS_OFF": {
        "primary": "The ending lost energy — the last note should sound as full as the first.",
        "variants": [
            "Energy faded toward the end — keep your support strong through bar 8.",
            "The final bars lost power — pace your breath so you finish strong.",
        ],
    },
    "L4_VOWEL_SHIFTS_PEAKS": {
        "primary": "Your vowel changed between the two peaks — keep it consistent even as pitch goes higher in bar 6.",
        "variants": [
            "The vowel was different at the two high points — maintain the same shape at both.",
            "Keep the vowel steady at both peaks — higher pitch shouldn't change the vowel.",
        ],
    },
    "L4_CLIMAX_NOT_REACHED": {
        "primary": "Bar 6 is meant to be the climax — bring a bit more intensity there than in bar 2.",
        "variants": [
            "The second peak should be bigger than the first — build more energy at bar 6.",
            "Give bar 6 more weight — it's the high point of the whole phrase.",
        ],
    },
    "L4_ROUGH_TRANSITIONS": {
        "primary": "There are a few rough transitions within the phrase — keep the legato connection smooth throughout.",
        "variants": [
            "Some note changes were bumpy — aim for seamless connections throughout.",
            "The transitions need smoothing — every note should flow into the next.",
        ],
    },

    # ── Level 4: 4.5 Simple Vocalises ─────────────────────────────────────
    "L4_REATTACK_SKIPS": {
        "primary": "The skips are getting re-attacked — keep the same continuous airflow across the leap as you would on a step.",
        "variants": [
            "Don't re-attack at the leaps — let the air flow just like on a stepwise motion.",
            "The leaps have gaps — treat them like steps and keep the sound connected.",
        ],
    },
    "L4_NO_DYNAMIC_SHAPING": {
        "primary": "Shape the phrase — a gentle rise to the peak, then ease back down.",
        "variants": [
            "The phrase was dynamically flat — add a subtle arc toward the top note.",
            "Give the phrase some shape — swell up to 'sol' and soften back.",
        ],
    },
    "L4_VOWEL_SWITCHES": {
        "primary": "Your vowel shifted partway through — stick with the one you chose for the whole phrase.",
        "variants": [
            "The vowel changed mid-phrase — maintain the same vowel throughout.",
            "Keep one vowel for the entire vocalise — it shifted as you went.",
        ],
    },
    "L4_BREATH_FAILS_FINAL": {
        "primary": "You ran out of breath just before the final note — take a fuller breath since this is sung in one breath.",
        "variants": [
            "The last note lost support — you need more air at the start for this one-breath phrase.",
            "Breath failed at the end — fill up more deeply before starting.",
        ],
    },
}


# ── Positive feedback for clean takes ─────────────────────────────────────

POSITIVE_GENERAL = [
    "Clean take — no errors detected. Nice work!",
    "That sounded great — everything was on target.",
    "Solid performance — pitch, timing, and support all looked good.",
    "Well done — keep it up at this level.",
    "No issues found — you nailed it.",
]


def get_feedback_text(error_id, params=None):
    """Return one feedback string for the given error_id, choosing
    randomly between primary and variants to avoid repetition."""
    entry = FEEDBACK.get(error_id)
    if not entry:
        return None
    pool = [entry["primary"]] + entry.get("variants", [])
    text = random.choice(pool)
    if params:
        try:
            text = text.format(**params)
        except (KeyError, IndexError):
            pass
    return text


def get_positive_feedback():
    """Return a general positive-feedback string for a clean take."""
    return random.choice(POSITIVE_GENERAL)


def is_positive(error_id):
    """Return True if this error_id represents positive (not-an-error) feedback."""
    entry = FEEDBACK.get(error_id)
    return bool(entry and entry.get("positive"))
