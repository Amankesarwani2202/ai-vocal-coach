"""
Three-Stage Exercise Flow Component
Manages: Introduction -> Recording -> Results stages
"""

import io
import wave
import numpy as np
import streamlit as st
from pathlib import Path


def init_exercise_flow():
    if "exercise_stage" not in st.session_state:
        st.session_state.exercise_stage = "introduction"
    if "exercise_recording_complete" not in st.session_state:
        st.session_state.exercise_recording_complete = False
    if "current_exercise_page" not in st.session_state:
        st.session_state.current_exercise_page = None
    if "recorded_audio" not in st.session_state:
        st.session_state.recorded_audio = None
    if "exercise_analysis" not in st.session_state:
        st.session_state.exercise_analysis = None


def reset_for_new_exercise(exercise_id):
    if st.session_state.get("current_exercise_page") != exercise_id:
        st.session_state.current_exercise_page = exercise_id
        st.session_state.exercise_stage = "introduction"
        st.session_state.exercise_recording_complete = False
        st.session_state.recorded_audio = None
        st.session_state.exercise_analysis = None


def reset_exercise_flow():
    st.session_state.exercise_stage = "introduction"
    st.session_state.exercise_recording_complete = False
    st.session_state.recorded_audio = None
    st.session_state.exercise_analysis = None


def move_to_recording():
    st.session_state.exercise_stage = "recording"


def move_to_results():
    st.session_state.exercise_stage = "results"
    st.session_state.exercise_recording_complete = True


def render_stage_indicator(current_stage):
    stages = [("introduction", "Prepare"), ("recording", "Record"), ("results", "Results")]
    parts = []
    for i, (key, label) in enumerate(stages):
        if key == current_stage:
            css_class = "stage-step active"
        elif [k for k, _ in stages].index(key) < [k for k, _ in stages].index(current_stage):
            css_class = "stage-step done"
        else:
            css_class = "stage-step"
        parts.append(f'<span class="{css_class}">{label}</span>')
        if i < len(stages) - 1:
            parts.append('<span class="stage-sep"></span>')
    st.markdown(f'<div class="stage-bar">{"".join(parts)}</div>', unsafe_allow_html=True)


def _check_noise_level(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            frames = wf.readframes(wf.getnframes())
            samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if len(samples) == 0:
            return False
        rms = np.sqrt(np.mean(samples ** 2))
        return rms > 3000
    except Exception:
        return False


def _generated_exhalation_audio():
    """Create a fallback 15-second breath reference when the WAV is absent."""
    samples = np.random.default_rng(7).normal(0, 0.12, 15 * 16000)
    samples = np.clip(samples, -1.0, 1.0)
    audio = (samples * 32767).astype(np.int16)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(16000)
        wav_file.writeframes(audio.tobytes())
    return buffer.getvalue()


def render_introduction_stage(exercise_info):
    level = exercise_info.get("level", "")
    clean_title = exercise_info.get("title", "Exercise")
    title_parts = clean_title.split(" ", 1)
    ex_num = title_parts[0]
    display_title = title_parts[1] if len(title_parts) > 1 else clean_title

    difficulty = exercise_info.get("difficulty", "")
    duration = exercise_info.get("duration_minutes", 0)
    skills = exercise_info.get("skills", [])

    st.markdown(f"""
    <div class="exercise-hero">
        <div class="exercise-number">Exercise {ex_num} &nbsp;·&nbsp; Level {level}</div>
        <h1>{display_title}</h1>
        <p class="subtitle">{exercise_info.get('description', '')}</p>
        <div class="exercise-meta">
            <span class="exercise-meta-item"><strong>Difficulty</strong>&nbsp; {difficulty}</span>
            <span class="exercise-meta-item"><strong>Duration</strong>&nbsp; ~{duration} min</span>
            {"".join(f'<span class="exercise-meta-item"><strong>Skill</strong>&nbsp; {s}</span>' for s in skills[:2])}
        </div>
    </div>
    """, unsafe_allow_html=True)

    exemplar = exercise_info.get("exemplar_asset")
    if exemplar:
        asset_path = Path(__file__).resolve().parent.parent / exemplar
        if asset_path.exists():
            st.markdown("""
            <div class="exemplar-block">
                <div class="exemplar-label">Listen to an example first</div>
            </div>
            """, unsafe_allow_html=True)
            with open(asset_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")
            st.caption("This is what a good attempt sounds like. Listen before you start.")
        else:
            st.markdown('<div class="notice-box">Audio example not yet available for this exercise.</div>', unsafe_allow_html=True)

    st.divider()

    st.markdown("**How to do it**")
    instructions = exercise_info.get("instructions", [])
    if instructions:
        steps_html = ""
        for i, step in enumerate(instructions, 1):
            steps_html += f'<div class="instruction-step"><span class="step-number">{i}</span><span class="step-text">{step}</span></div>'
        st.markdown(steps_html, unsafe_allow_html=True)

    st.divider()

    if st.button("Start exercise", use_container_width=False, key="start_exercise"):
        move_to_recording()
        st.rerun()


_RECORDING_FOCUS = {
    "scale_ascending":    "Direct attack on every note — no scooping. Top 'do' as clear as the first.",
    "scale_descending":   "Keep breath support up throughout the descent — don't let it sag.",
    "minor_scale":        "Keep minor 3rd and 7th in place — don't sharpen toward major.",
    "intervals":          "Hear the target note in your head before the leap, then attack directly.",
    "arpeggios":          "Let the voice lighten toward the top — don't force chest voice past the break.",
    "pitch_stability":    "Set pitch immediately; hold breath pressure constant for the full 6–8 s.",
    "vowel_sustain":      "Fix mouth shape before the note — identical at start, middle, and end.",
    "vowel_ascending":    "Fix jaw and tongue on note 1; do not let the shape change as pitch rises.",
    "vowel_modification": "Open 'ah' toward 'aw' at the break — subtle, gradual, never a full swap.",
    "consonant_clarity":  "Consonant quick, vowel pure — the 5th repetition as crisp as the 1st.",
    "tongue_tension":     "Tongue tip rests against lower teeth — no gripping at the back.",
    "diction_challenge":  "Word-ending consonants ('l', 'n') must be as clear when sung as when spoken.",
    "legato_notes":       "No click, gap, or re-attack — one continuous airstream through do-re-mi.",
    "legato_melody":      "One sustained idea that changes pitch, not five separate attempts.",
    "breath_phrasing":    "Breath at bar-end only — never mid-bar.",
    "melodic_etude":      "Final note as supported and clear as the very first.",
    "vocalises":          "Continuous airflow through both leaps — resist re-attacking each note.",
    "scale":              "Pitch changes are expected — focus on landing each step cleanly.",
    "staccato":           "Staccato = clear silence between notes; legato = one unbroken line.",
    "legato":             "Airflow continuous between notes — no gaps or re-attacks.",
    "range_finder":       "Start in your middle voice, then step up and down to find your edges.",
    "smooth_onset":       "Start each note cleanly — no breathy lead-in or hard glottal attack.",
}

_RECORDING_TARGET = {
    "scale_ascending":    "do · re · mi · fa · sol · la · ti · do (8 ascending notes, one per beat)",
    "scale_descending":   "do · ti · la · sol · fa · mi · re · do (8 descending, one per beat)",
    "minor_scale":        "la · ti · do · re · mi · fa · sol · la (natural minor, one per beat)",
    "intervals":          "Low note → leap to high note (direct attack, no slide)",
    "arpeggios":          "do · mi · sol · do · sol · mi · do (triad arpeggio, one per beat)",
    "pitch_stability":    "Single note sustained for 6–8 seconds",
    "vowel_sustain":      "A (ah) · E (eh) · I (ee) · O (oh) · U (oo) — 3–4 s per vowel",
    "vowel_ascending":    "do · re · mi · fa · sol on 'ah' — ascending, one per beat",
    "vowel_modification": "do · re · mi · fa · sol — ascending through the passaggio",
    "consonant_clarity":  "Na × 5 · Ma × 5 · La × 5 · Ra × 5 at steady moderate tempo",
    "tongue_tension":     "'ah' 5 s · 'ee' 5 s · 'oo' 5 s — three vowel rounds",
    "diction_challenge":  "Speak phrase · then sing sol · fa · mi · re · do on the same phrase",
    "legato_notes":       "do · re · mi on 'ah' — 3 connected notes, one breath",
    "legato_melody":      "do · re · mi · re · do on 'ah' — 5 notes with a volume arc",
    "breath_phrasing":    "4-bar melody (bars 1–2 + bars 3–4) in one or at most two breaths",
    "melodic_etude":      "8-bar étude: bars 1–4 (one breath), bars 5–8 (second breath)",
    "vocalises":          "do · mi · sol · mi · do on 'ah' or 'oo' — one breath",
    "scale":              "do · re · mi · fa · sol · fa · mi · re · do, one per beat",
    "staccato":           "do · re · mi · fa · sol (staccato), then same notes legato",
    "legato":             "do · re · mi · re · do on 'oo' — connected in one breath",
}


def _render_compact_recording_cues(exercise_type, exercise_info, detailed_instructions):
    """Compact pre-recording reminder card: pattern + 3 key cues + focus item."""
    target = _RECORDING_TARGET.get(exercise_type)
    focus = _RECORDING_FOCUS.get(exercise_type, "Follow the exercise instructions.")

    # Skip table rows (lines beginning with "|"); take the last 3 actionable cues
    non_table = [i for i in detailed_instructions if not i.strip().startswith("|")]
    key_cues = non_table[-3:]

    st.markdown("**Before you record**")

    if target:
        st.markdown(
            f'<p style="font-size:0.85rem;color:var(--text-muted,#6B6560);margin:0 0 0.5rem 0">'
            f'<strong>Pattern:</strong> {target}</p>',
            unsafe_allow_html=True,
        )

    if key_cues:
        cue_lines = "".join(f"<li style='margin-bottom:0.3rem'>{c}</li>" for c in key_cues)
        st.markdown(
            f'<ul style="margin:0 0 0.5rem 1.1rem;padding:0;font-size:0.9rem">{cue_lines}</ul>',
            unsafe_allow_html=True,
        )

    st.info(f"**Focus:** {focus}")

    with st.expander("View all instructions", expanded=False):
        for idx, instruction in enumerate(detailed_instructions, 1):
            if not instruction.strip().startswith("|"):
                st.markdown(f"**{idx}.** {instruction}")
        # Render any embedded table rows together
        table_rows = [r for r in detailed_instructions if r.strip().startswith("|")]
        if table_rows:
            st.markdown("\n".join(table_rows))


def render_recording_stage(exercise_id, breathing_type="support"):
    from components.breathing_guide import render_breathing_guide
    from components.exercise_guides import render_exercise_guide
    from engine.audio_analysis import exercise_type_from_id, analyze_audio, generate_click_track

    exercise_type = exercise_type_from_id(exercise_id)
    is_major_scale_ascending = exercise_type == "scale_ascending"

    if st.session_state.get("noise_warning_shown") and not st.session_state.get("noise_continue"):
        st.markdown("""
        <div class="noise-warning">
            <strong>Your environment is noisy.</strong> Move somewhere quieter for more accurate feedback.
        </div>
        """, unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Try again", key="noise_retry", use_container_width=True):
                st.session_state.noise_warning_shown = False
                st.rerun()
        with col2:
            if st.button("Continue anyway", key="noise_continue_btn", use_container_width=True):
                st.session_state.noise_continue = True
                st.rerun()
        return None

    if exercise_type in {"warm_up", "breath_support", "silent_breath"}:
        render_breathing_guide(exercise_type)
    else:
        from utils.pages_config import get_page_info
        from utils.detailed_instructions import get_detailed_instructions
        exercise_info = get_page_info(exercise_id) or {}
        detailed = get_detailed_instructions(exercise_id)

        if detailed:
            # Compact cue card: pattern + 3 key reminders + focused tip
            _render_compact_recording_cues(exercise_type, exercise_info, detailed)
        else:
            # Fall back to animated guide + instructions for exercises without detailed content
            render_exercise_guide(exercise_type)
            fallback_instructions = exercise_info.get("instructions", [])
            if fallback_instructions:
                with st.expander("Exercise instructions", expanded=False):
                    for number, instruction in enumerate(fallback_instructions, 1):
                        st.markdown(f"**{number}.** {instruction}")
            fallback_focus = _RECORDING_FOCUS.get(
                exercise_type,
                "Follow the exercise instructions while recording.",
            )
            st.markdown("**Your focus**")
            st.info(fallback_focus)
            if exercise_type == "staccato":
                with st.expander("What do staccato and legato mean?"):
                    st.markdown(
                        "**Staccato** means short, separated notes. "
                        "**Legato** means smooth, connected notes."
                    )

    # Exhalation reference audio (exercise-specific, e.g. 0.1)
    from utils.pages_config import get_page_info
    _einfo = get_page_info(exercise_id)
    _exh = _einfo.get("exhalation_asset") if _einfo else None
    if _exh:
        _exh_path = Path(__file__).resolve().parent.parent / _exh
        if _exh_path.exists():
            with open(_exh_path, "rb") as _f:
                _exh_audio = _f.read()
        else:
            _exh_audio = _generated_exhalation_audio()

        if _exh_audio:
            st.markdown(
                '<div class="exemplar-block" style="margin-top:0.5rem">'
                '<div class="exemplar-label">Exhalation reference</div>'
                '</div>',
                unsafe_allow_html=True,
            )
            st.audio(_exh_audio, format="audio/wav")

    st.divider()

    _BEAT_SENSITIVE_TYPES = {
        "scale_ascending", "scale_descending", "minor_scale", "intervals", "arpeggios",
        "scale", "staccato", "legato", "smooth_onset", "vowel_ascending",
        "vowel_modification", "legato_notes", "legato_melody", "breath_phrasing",
        "melodic_etude", "vocalises",
    }
    needs_count_in = exercise_type in _BEAT_SENSITIVE_TYPES

    import time as _time

    # --- 3-2-1 countdown state machine ---
    countdown_key = f"countdown_active_{exercise_id}"
    ready_key = f"recording_ready_{exercise_id}"

    st.markdown("**Record your attempt**")

    if not st.session_state.get(ready_key):
        # Show "Get ready" button which triggers the countdown
        btn_label = "Start count-in & record" if needs_count_in else "Get ready (3-2-1)"
        if st.button(btn_label, key=f"start_countdown_{exercise_id}", use_container_width=True):
            st.session_state[countdown_key] = True
            st.rerun()

        if st.session_state.get(countdown_key):
            # Visual 3-2-1 countdown
            _cd_slot = st.empty()
            for _n in (3, 2, 1):
                _cd_slot.markdown(
                    f'<div style="text-align:center;font-size:4rem;font-weight:700;'
                    f'padding:1rem 0;color:var(--primary-color,#0f766e)">{_n}</div>',
                    unsafe_allow_html=True,
                )
                _time.sleep(1)
            _cd_slot.empty()
            st.session_state[countdown_key] = False
            st.session_state[ready_key] = True
            st.rerun()

        col_cancel, _ = st.columns([1, 3])
        with col_cancel:
            if st.button("Cancel", key="rec_cancel"):
                reset_exercise_flow()
                st.rerun()
        return None

    # Countdown done — show recording UI
    if needs_count_in:
        if st.session_state.get(f"count_in_ready_{exercise_id}"):
            st.markdown(
                '<div class="count-in" role="status"><strong>Count-in ready</strong> · 1 · 2 · 3 · 4</div>',
                unsafe_allow_html=True,
            )
        st.audio(generate_click_track(bpm=60, bars=8, beats_per_bar=4), format="audio/wav")
        st.caption(
            "Count-in is playing. Press the microphone button to start recording. "
            "Use headphones so the click is not captured in the analysis."
        )
    else:
        st.caption("Press the microphone button below to record. Press stop when you're done.")

    audio_input = st.audio_input("Record", key=f"audio_rec_{exercise_id}", label_visibility="hidden")

    if audio_input is not None:
        audio_bytes = audio_input.read()

        if not st.session_state.get("noise_continue") and not st.session_state.get("noise_warning_shown"):
            if _check_noise_level(audio_bytes):
                st.session_state.noise_warning_shown = True
                st.rerun()

        _render_waveform(audio_bytes, st.session_state.get("exercise_analysis"))
        _render_analysis_snapshot(st.session_state.get("exercise_analysis"))

        st.markdown("")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Try again", use_container_width=True, key="rec_retry"):
                st.session_state.noise_warning_shown = False
                st.session_state.noise_continue = False
                st.session_state.exercise_analysis = None
                st.session_state[f"recording_ready_{exercise_id}"] = False
                st.rerun()
        with col2:
            if st.button("Submit recording", use_container_width=True, key="rec_submit"):
                st.session_state.recorded_audio = audio_bytes
                with st.spinner("Analysing your recording…"):
                    st.session_state.exercise_analysis = analyze_audio(audio_bytes, exercise_type)
                move_to_results()
                st.rerun()

        return audio_bytes

    col_cancel, _ = st.columns([1, 3])
    with col_cancel:
        if st.button("Cancel", key="rec_cancel"):
            reset_exercise_flow()
            st.rerun()

    return None


def _render_analysis_snapshot(analysis):
    """Show the most useful measurements immediately after analysis."""
    if not analysis or not analysis.get("subscores"):
        return

    st.markdown("**What the coach heard**")
    columns = st.columns(min(3, len(analysis["subscores"])))
    for column, (label, value) in zip(columns, list(analysis["subscores"].items())[:3]):
        column.metric(label, f"{value}/100")


def _render_waveform(audio_bytes, analysis=None):
    """Render amplitude waveform with optional pitch overlay from analysis."""
    try:
        import plotly.graph_objects as go

        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            n_frames = wf.getnframes()
            framerate = wf.getframerate()
            frames = wf.readframes(n_frames)

        samples = np.frombuffer(frames, dtype=np.int16).astype(np.float32)
        if len(samples) == 0:
            return

        step = max(1, len(samples) // 400)
        samples_ds = samples[::step]
        duration = n_frames / framerate
        times = np.linspace(0, duration, len(samples_ds))

        peak = np.max(np.abs(samples_ds)) or 1
        samples_norm = samples_ds / peak

        fig = go.Figure()

        # Amplitude waveform
        fig.add_trace(go.Scatter(
            x=times, y=samples_norm,
            mode="lines",
            line=dict(color="rgba(180,83,9,0.5)", width=1),
            hoverinfo="skip",
            name="Amplitude",
        ))

        # Pitch overlay from analysis if available
        if analysis and analysis.get("pitch_data"):
            pd = analysis["pitch_data"]
            f0_raw = pd.get("f0", [])
            t_raw  = pd.get("times", [])
            if f0_raw and t_raw:
                f0_arr = np.array([v if v is not None else np.nan for v in f0_raw])
                t_arr  = np.array(t_raw)
                # Normalise f0 to [-1, 1] for overlay
                valid = ~np.isnan(f0_arr)
                if np.sum(valid) > 2:
                    f0_min = np.nanmin(f0_arr)
                    f0_max = np.nanmax(f0_arr)
                    f0_rng = f0_max - f0_min or 1
                    f0_norm = np.where(valid, (f0_arr - f0_min) / f0_rng * 2 - 1, np.nan)
                    fig.add_trace(go.Scatter(
                        x=t_arr, y=f0_norm,
                        mode="lines",
                        line=dict(color="rgba(74,155,111,0.85)", width=2),
                        connectgaps=False,
                        name="Pitch",
                        hovertemplate="Pitch: %{customdata:.0f} Hz<extra></extra>",
                        customdata=f0_arr,
                    ))

        fig.update_layout(
            height=90,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(visible=False),
            yaxis=dict(visible=False, range=[-1.1, 1.1]),
            showlegend=bool(analysis and analysis.get("pitch_data", {}).get("f0")),
            legend=dict(
                orientation="h", x=0, y=1.15,
                font=dict(size=10),
                bgcolor="rgba(0,0,0,0)",
            ),
        )
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption(f"Recording: {duration:.1f}s" + (" · amber = amplitude · green = pitch" if analysis else ""))
    except Exception:
        pass


def _render_pitch_target_chart(analysis, exercise_id):
    """Compare recorded pitch with the expected scale or arpeggio shape."""
    if not analysis or not analysis.get("pitch_data"):
        return

    from engine.audio_analysis import exercise_type_from_id

    patterns = {
        "scale_ascending":  [0, 2, 4, 5, 7, 9, 11, 12],
        "scale_descending": [12, 11, 9, 7, 5, 4, 2, 0],
        "minor_scale":      [0, 2, 3, 5, 7, 8, 10, 12],
        "arpeggios":        [0, 4, 7, 12, 7, 4, 0],
        "intervals":        [0, 7],
        "legato_notes":     [0, 2, 4, 2, 0],
        "legato_melody":    [0, 2, 4, 5, 7, 5, 4, 2, 0],
        "vowel_ascending":  [0, 2, 4, 5, 7],
        "scale":            [0, 2, 4, 5, 7],
        "melodic_etude":    [0, 2, 4, 5, 7, 9, 11, 12, 11, 9, 7, 5, 4, 2, 0],
        "vocalises":        [0, 4, 7, 4, 0],
        "breath_phrasing":  [0, 2, 4, 5, 7, 9, 7, 5, 4, 2, 0],
    }
    pattern = patterns.get(exercise_type_from_id(exercise_id))
    if not pattern:
        return

    try:
        import plotly.graph_objects as go

        pitch_data = analysis["pitch_data"]
        times = np.asarray(pitch_data.get("times", []), dtype=float)
        f0 = np.asarray(
            [value if value is not None else np.nan for value in pitch_data.get("f0", [])],
            dtype=float,
        )
        valid = np.isfinite(times) & np.isfinite(f0) & (f0 > 0)
        if np.sum(valid) < 6:
            return

        actual_times = times[valid]
        actual_f0 = f0[valid]
        anchor = float(np.median(actual_f0[: max(3, len(actual_f0) // 8)]))
        if anchor <= 0:
            return

        duration = float(max(actual_times[-1], 0.1))
        note_times = np.linspace(0, duration, len(pattern))
        target_f0 = anchor * (2.0 ** (np.asarray(pattern, dtype=float) / 12.0))
        target_at_actual = np.interp(actual_times, note_times, target_f0)
        deviation_cents = np.abs(1200.0 * np.log2(actual_f0 / target_at_actual))
        wavering = deviation_cents > 70

        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=actual_times,
            y=actual_f0,
            mode="lines",
            name="Your pitch",
            line=dict(color="#2563eb", width=2),
            connectgaps=False,
            hovertemplate="Your pitch: %{y:.0f} Hz<extra></extra>",
        ))
        fig.add_trace(go.Scatter(
            x=note_times,
            y=target_f0,
            mode="lines+markers",
            name="Target shape",
            line=dict(color="#c2410c", width=2, dash="dash"),
            marker=dict(size=7),
            hovertemplate="Target: %{y:.0f} Hz<extra></extra>",
        ))
        if np.any(wavering):
            fig.add_trace(go.Scatter(
                x=actual_times[wavering],
                y=actual_f0[wavering],
                mode="markers",
                name="Needs attention",
                marker=dict(color="#dc2626", size=6),
                hovertemplate="Away from target<extra></extra>",
            ))

        fig.update_layout(
            height=260,
            margin=dict(l=0, r=0, t=10, b=0),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Time",
            yaxis_title="Pitch (Hz)",
            legend=dict(orientation="h", y=1.12),
        )
        st.markdown("**Pitch against the target shape**")
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.caption("Blue is your pitch, orange is the expected pattern, and red marks larger deviations from the target.")
    except Exception:
        return


def _recording_duration_seconds(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes), 'rb') as wf:
            return wf.getnframes() / wf.getframerate()
    except Exception:
        return None


def _timestamp_to_seconds(ts):
    try:
        parts = str(ts).split(":")
        return int(parts[0]) * 60 + float(parts[1])
    except Exception:
        return 0.0


def render_results_stage(exercise_id, next_page):
    """
    Render results using real analysis from st.session_state.exercise_analysis.
    Includes score, waveform playback, timestamped feedback, coaching summary,
    and save-and-continue / try-again buttons.
    """
    from utils.state import add_score

    analysis = st.session_state.get("exercise_analysis") or {}

    score = analysis.get("score", 0)
    xp    = analysis.get("xp", 0)
    raw_feedback = analysis.get("feedback", [])
    subscores    = analysis.get("subscores", {})

    # Score badge
    if score >= 85:
        score_label, score_class = "Excellent", "score-good"
    elif score >= 70:
        score_label, score_class = "Good", "score-ok"
    else:
        score_label, score_class = "Keep practising", "score-low"

    col1, col2 = st.columns([3, 1])
    with col1:
        st.markdown(f"""
        <div style="margin-bottom:0.25rem">
            <span style="font-size:2rem;font-weight:700;letter-spacing:-0.02em">{score}</span>
            <span style="font-size:1rem;color:var(--text-muted,#6B6560)">/100</span>
        </div>
        <span class="score-badge {score_class}">{score_label}</span>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div style="text-align:right;padding-top:0.5rem">
            <div style="font-size:1.1rem;font-weight:700">+{xp} XP</div>
            <div style="font-size:0.75rem;color:var(--text-muted,#6B6560)">earned</div>
        </div>
        """, unsafe_allow_html=True)

    # Subscores
    if subscores:
        st.markdown("")
        cols = st.columns(len(subscores))
        for col, (dim, val) in zip(cols, subscores.items()):
            col.metric(dim, f"{val}/100")

    from engine.audio_analysis import exercise_type_from_id
    exercise_type = exercise_type_from_id(exercise_id)

    # Recorded audio playback
    recorded = st.session_state.get("recorded_audio")
    rec_duration = None
    if recorded:
        st.markdown("**Your recording**")
        st.audio(recorded, format="audio/wav")
        rec_duration = _recording_duration_seconds(recorded)

        _CHART_TYPES = {
            "scale_ascending", "scale_descending", "minor_scale", "arpeggios",
            "intervals", "legato_notes", "legato_melody", "vowel_ascending",
            "scale", "melodic_etude", "vocalises", "breath_phrasing",
        }
        if exercise_type in _CHART_TYPES:
            _render_pitch_target_chart(analysis, exercise_id)

    st.divider()

    # Filter feedback to actual recording duration
    if rec_duration is not None:
        feedback_list = [
            f for f in raw_feedback
            if not isinstance(f, dict) or _timestamp_to_seconds(f.get("time", "0:00")) <= rec_duration
        ]
        if not feedback_list and raw_feedback:
            feedback_list = [{"time": "", "message": "Recording was too short for detailed feedback. Try holding notes longer."}]
    else:
        feedback_list = raw_feedback

    feedback_list = sorted(
        feedback_list,
        key=lambda item: (
            _timestamp_to_seconds(item.get("time", "0:00"))
            if isinstance(item, dict)
            else 0.0
        ),
    )

    if feedback_list:
        st.markdown("**Feedback**")

        # Group repeated messages — collect all timestamps per normalised message text.
        import re as _re
        _grouped: dict = {}  # normalised_msg -> {"display": str, "times": list[str]}
        _ungrouped = []      # items that have no timestamp (plain strings)
        for _item in feedback_list:
            if isinstance(_item, dict):
                _msg = _item.get("message", "")
                _t   = _item.get("time", "")
                _key = _re.sub(r'\s+', ' ', _msg.strip().lower())
                if _key:
                    if _key not in _grouped:
                        _grouped[_key] = {"display": _msg.strip(), "times": []}
                    if _t:
                        _grouped[_key]["times"].append(_t)
            else:
                _ungrouped.append(str(_item))

        items_html = ""
        for _entry in _grouped.values():
            _disp = _entry["display"]
            _times = _entry["times"]
            if len(_times) > 1:
                _ts_str = " · ".join(
                    f'<span class="feedback-timestamp">{_t}</span>' for _t in _times
                )
                items_html += (
                    f'<div class="feedback-item">'
                    f'<span class="feedback-text">{_disp}</span>'
                    f'<div style="margin-top:0.2rem;font-size:0.8rem">{_ts_str}</div>'
                    f'</div>'
                )
            elif _times:
                items_html += (
                    f'<div class="feedback-item">'
                    f'<span class="feedback-timestamp">{_times[0]}</span>'
                    f'<span class="feedback-text">{_disp}</span>'
                    f'</div>'
                )
            else:
                items_html += (
                    f'<div class="feedback-item">'
                    f'<span class="feedback-text">{_disp}</span>'
                    f'</div>'
                )
        for _s in _ungrouped:
            items_html += f'<div class="feedback-item"><span class="feedback-text">{_s}</span></div>'

        st.markdown(items_html, unsafe_allow_html=True)

    st.divider()

    # Coaching summary
    from engine.coaching import generate_coaching_summary
    summary       = generate_coaching_summary(
        score,
        feedback_list,
        subscores,
        exercise_type=exercise_type,
    )
    what_went_well = summary.get("what_went_well", [])
    work_on        = summary.get("work_on", [])
    next_time      = summary.get("next_time", "")

    if what_went_well or work_on or next_time:
        st.markdown("**Coaching summary**")
        if what_went_well:
            items = "".join(f"<li>{i}</li>" for i in what_went_well)
            st.markdown(f'<div class="coaching-section"><div class="coaching-section-label">What went well</div><ul style="margin:0.25rem 0 0 1.2rem">{items}</ul></div>', unsafe_allow_html=True)
        if work_on:
            items = "".join(f"<li>{i}</li>" for i in work_on)
            st.markdown(f'<div class="coaching-section"><div class="coaching-section-label">Focus on next time</div><ul style="margin:0.25rem 0 0 1.2rem">{items}</ul></div>', unsafe_allow_html=True)
        if next_time:
            st.markdown(f'<div class="coaching-section"><div class="coaching-section-label">Recommendation</div><p style="margin:0.25rem 0 0 0">{next_time}</p></div>', unsafe_allow_html=True)

    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Try again", use_container_width=True, key=f"retry_{exercise_id}"):
            reset_exercise_flow()
            st.rerun()
    with col_b:
        is_final_exercise = next_page == "pages/1_Dashboard.py"
        action_label = "Finish" if is_final_exercise else "Save and continue"
        if st.button(action_label, use_container_width=True, key=f"save_score_{exercise_id}"):
            add_score(exercise_id, score, xp)
            st.session_state.exercise_analysis = None
            st.toast("Progress saved")
            reset_exercise_flow()
            st.switch_page(next_page)

    if st.button("View progress", use_container_width=True, key=f"progress_{exercise_id}"):
        st.switch_page("pages/1_Dashboard.py")
