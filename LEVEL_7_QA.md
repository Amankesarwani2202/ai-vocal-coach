# Level 7 feedback implementation and validation

Source: Vocal-Coach-Level-7-Fix-Spec.docx, supplied for PR #4. This revision implements the five exercise patterns, exercise-specific analysis, a capstone and a completion experience. Automated validation is complete; live sung-recording acceptance remains open. Items below distinguish implemented checks from measurements that require additional calibration or account infrastructure. No team sign-off is assumed for these limitations.

## Critical fixes

| Feedback | Change | Verification |
| --- | --- | --- |
| A1 Tracking loss scored as a crack | Only adjacent confident pitch samples can establish a discontinuity. Tracking-loss windows produce neutral advice and do not reduce connection scores. Quiet gaps are separate acoustic evidence. | Injected tracking dropouts in 7.1 and 7.2 leave connection scores unchanged. |
| A2 Reused score labels | 7.1 uses Pitch Connection and Arrival Accuracy. 7.2 uses Register Release, RMS-based Support Through Return and measurable Vowel Brightness Contrast. Discrete written steps are excluded from break detection. | Reference and Streamlit screen regressions. |
| A3 Generic ornamentation fallback | 7.3 has Grace Note Clarity, relative Beat Stability and Landing Accuracy. Confident pitch changes and energy entrances identify distinct grace/main attacks, including legato ornaments. Live capture supplies a shared count-in clock. Generic Voice Presence is never used for Level 7. | Correct above/below ornaments and a missing-ornament negative control. |
| A4 Cutoff artifacts | One valid-performance endpoint excludes the final half analysis frame from pitch/activity masks before every analyzer runs and from chart samples. The early-ending event uses the same detected endpoint (the analysis margin is reported in metadata). | Injected terminal pitch corruption cannot alter scores or charts; incomplete takes cannot save. |
| A5 Low fast-run targets | Anchor comes from the first note's early confident samples, with no arbitrary C4/noise fallback. Slow phase establishes the key. An average mismatch over one octave withholds pitch scoring, target display, remedial landing advice and progress. | Correct targets at C3, C4, G4 and C5; deliberate two-octave mismatch is rejected. |

## Exercise coverage

| Exercise | Pattern and feedback implemented | Remaining measurement limits |
| --- | --- | --- |
| 7.1 Portamento | Hold 0.5s, fifth up 2.5s, hold 0.5s, fifth down 2.5s, hold 0.5s. Starting-pitch selector or first sung note. Smoothness, connection, held arrival accuracy, start dip, rushed ascent and missing return checks. Playback and chart use the same segments. | No register-specific claims without a confirmed personal passaggio. |
| 7.2 Register Turning Points | C♯–D–E–F–G and return at 72 BPM on ah; repeat on eh. Genuine within-note discontinuities, return energy steadiness, F2 contrast, spectral observations, optional soft-reference comparison and optional centring on a user-supplied transition zone. | Range Finder cannot establish passaggio. Resonance Adjustment is withheld: spectral movement alone cannot prove natural release versus forcing. Optional soft-reference recording permits a same-microphone relative comparison; absolute vocal loudness remains unmeasured. No squeeze diagnosis. |
| 7.3 Ornamentation | A–G twice, F–G twice; 0.12s grace plus 0.83s main note at 72 BPM. Distinct grace/main attacks, duration/late landing, main pitch settling and both-direction checks. Grace notes borrow time from the preceding beat; main attacks are exactly one beat apart. | Beat Stability uses pitch-change/energy attacks and a shared count-in clock in live capture. Simple microphone mode uses relative timing. Sparse/unclear attacks withhold the score; device latency remains uncalibrated. |
| 7.4 Slow Melismas | C–D–E–F–G at 55 BPM, repeated at 48 BPM. Pitch Accuracy, Legato Continuity, measurable LPC Vowel Stability, Evenness and slower-repeat check. | Sparse LPC measurements explicitly withhold vowel scoring. |
| 7.5 Fast Runs | C–D–E–D–C at 60 BPM, repeat at 180 BPM; hold final tonic one second. The UI requires a separate slow take scoring at least 85/100 pitch accuracy and four stable notes before enabling fast recording. Active-phase playback and capture are separate; fast scoring retains the passed slow key and compares measured phase tempos and accuracy. Final held-note checks remain. | Jaw/tongue position and tension cannot be established from these recordings; listening guidance replaces a fabricated score. Unsupported phase timing withholds Tempo Progression. |
| 7.6 Capstone | 15–30s chosen phrase, planned breath times, recorded playback and mandatory pride reflection. Radar of available breath, legato, local pitch-control and dynamic-range measurements. No external pitch target, overall verdict, XP or stored numeric overall score. | Local pitch movement and dynamic range are acoustic proxies affected by intended melody; intentional musical shape requires listening. Diction Clarity is available as an attack-definition proxy when at least four syllable attacks are resolved; it is not word recognition. Breath matching is one-to-one, with unplanned pauses identified. Smoothed dynamic shape checks a sustained rise and fall. Word pronunciation, musical intent and mid-word breath detection still need listening. |

## Completion experience

- Capstone leads to a separate finish page. A full-course heading and certificate claim require all 42 active exercises; otherwise the page acknowledges capstone completion and shows exercises remaining.
- Journey includes completed exercises, XP, recorded practice time and start/finish dates. Practice time covers saved attempts tracked in this version; historical time is not invented.
- Repeated versioned metric evidence supplies up to three strengths and two areas to develop. Old unversioned scores, including the faulty Fast Runs results, are excluded.
- Downloadable navy/rust certificate PNG includes name, completion date, recorded practice and exercise count. Incomplete-course certificates describe the capstone only. Users can download to share.
- Revisit exercises or use the new unscored recording/playback practice page.
- Optional “Remember my progress on this browser” stores the progress schema and first-completion flag in browser localStorage, restoring them after session loss or Cloud reboot. Storage handshake prevents default session values from overwriting existing progress. Turning it off or clearing user data removes the browser copy. Audio is excluded. JSON backup remains available for device transfer or blocked browser storage. This is one local browser profile, not authenticated once-per-account or cross-device synchronization; shared browsers share that profile.

## Acceptance still required before launch

Use real sung recordings on 7.1–7.6, including mobile microphone capture and playback. The attached DOCX describes screenshots but supplies no source recordings; synthetic waveforms and injected failures cannot substitute for this acceptance pass.

1. Sing each complete reference at a comfortable transposition; inspect displayed targets, timing and score evidence.
2. Repeat 7.1/7.2 with a soft tracking dropout and a true audible crack; verify they receive different treatment.
3. Sing grace notes missing, overlong and from only one direction; compare against a clean take with the same key.
4. Stop 7.4 mid-note; confirm cutoff artifacts do not appear on its chart or change measured note values.
5. Sing 7.5 cleanly slow/fast, as a smeared slide, at constant tempo and with a rushed final note; compare the detectors with listening.
6. Finish the capstone, listen back, add a reflection and verify certificate wording, replay behavior and backup/restore on another visit.

This branch remains a review candidate until the real-recording pass and the scoped measurement/account limitations are accepted. No merge or deployment is performed by this change.

## Automated validation result

98 tests pass: the existing audio and Streamlit regressions, all 42 exercise prepare/record screens, 19 Level 7/completion regressions and 16 additional phase-gate, clock, progress-storage and capstone checks. Python compilation and whitespace checks pass. Tests use synthetic audio and injected tracking failures, not human microphone recordings. They establish implementation regressions, not clinical or pedagogical calibration of the acoustic proxies.

## Feasible Streamlit Cloud follow-up

- No server-local JSON/SQLite persistence is used: Streamlit Cloud filesystems are ephemeral and cannot safely distinguish public users by display name. Optional browser storage is per browser, with explicit opt-in, failure handling, schema validation and downloadable backups. Authenticated accounts require separately configured identity and durable database services.
- Optional user-supplied transition zones are practice references, not automatically diagnosed passaggi. Formant observations remain available; scoring natural resonance release versus forcing remains withheld.
- The recorder now provides a count-in for 7.3 and places the initial grace pickup before beat one. The onset detector includes confident pitch changes because legato grace notes may have no separate energy attack.
- Fast-run phase one must pass before phase two can be recorded in the UI. Failed slow takes cannot save progress; retry clears phase state and recorder keys.
- Real human recording acceptance and device-latency calibration remain open. Automated passing results are not presented as human-listening approval.
