# Supplied materials and QA changes

| Requirement | Implementation |
| --- | --- |
| Shared audio and scores | Imported WAV and PNG materials, with references available on introduction and recording screens. |
| Eight-second breath | Instructions, generated audio, animation and completion threshold agree. |
| Readable, accurate charts | Flat note targets, major thirds, descending anchor, distinct recorded/target/error colors. |
| Quiet starts and silence | Relative onset timeline; internal gaps only between confirmed voiced sections. |
| Staccato then legato | Separate five-note sections and measured articulation contrast. |
| Appropriate skill analysis | Held, stepped, glide, rhythm and free models; dynamic arcs, duration, spectral and vowel measurements. |
| Evidence and coaching | Measured evidence accompanies scores; explicit feedback valence, weakest/tied skills, catalog-verified recommendations. |
| Levels 2–5 rules | Scale landing/drift, leap/scoop, arpeggio continuity, LPC vowel changes, phrase boundaries, distinct beat grids, matching and note values. |
| Recording and retry | Instructions/reference replay, optional live cues, fresh take keys, incomplete take cannot save progress. |
| Retired content | Levels 8–9 removed from navigation/catalog/pages/progress; 7.5 leads to 7.6 Capstone and then the course finish page. |

## Source discrepancies

- Supplied 1.5 audio and score use do–re–mi–re–do; the guide now matches them.
- Supplied 2.3 recording uses harmonic minor. It is retained as a labeled alternate; the primary generated reference matches the requested natural minor.
- Supplied 2.5 holds the upper do for two beats; the target grid matches this timing.
- Piano examples demonstrate notes, not normative vocal articulation, formants or breath technique. Reverberation can conceal staccato gaps.

## Measurement limits

Audio cannot establish anatomical placement, projection, tongue/jaw position, chest mechanism or an individual passaggio. These claims are withheld rather than scored. Vowel spectral changes and brightness are acoustic proxies; per-word intelligibility has no calibrated alignment model. Absolute syncopation phase requires the live recorder's shared clock; simple microphone recordings receive relative timing feedback only. Microphone/device latency is not calibrated. Live cues are advisory and final analysis is performed after capture.

Regression tests cover synthetic audio signals and all active Streamlit exercise pages. Real microphone/browser capture was not verified end to end because the browser session stalled; device permission, capture and playback require a manual smoke test before merging.

## Level 7 follow-up

See [LEVEL_7_QA.md](LEVEL_7_QA.md) for every supplied Level 7 item, regression coverage and remaining live-recording/account/calibration acceptance. The active curriculum now has 42 exercises including 7.6 Capstone Performance.
