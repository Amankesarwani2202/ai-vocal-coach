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


def render_recording_stage(exercise_id, breathing_type="support"):
    from components.breathing_guide import render_breathing_guide
    from components.exercise_guides import render_exercise_guide
    from engine.audio_analysis import exercise_type_from_id, analyze_audio

    exercise_type = exercise_type_from_id(exercise_id)

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
        render_exercise_guide(exercise_type)
        guidance = {
            "range_finder": (
                "Sing one comfortable note, then step upward and downward. "
                "Stop at the highest and lowest notes you can sing comfortably."
            ),
            "smooth_onset": (
                "Sing five light 'la' or 'ma' notes on one pitch. "
                "Start each note cleanly without a breathy or harsh attack."
            ),
            "legato": (
                "Sing do-re-mi-re-do on 'oo' as one connected phrase. "
                "Keep the airflow moving between notes."
            ),
            "scale": (
                "Sing do-re-mi-fa-sol on 'oo'. Keep each note clear "
                "while maintaining steady breath support."
            ),
            "staccato": (
                "First sing do-do-do as short, separated notes. Then repeat "
                "the pattern smoothly connected, noticing the contrast."
            ),
        }
        st.markdown("**Your focus**")
        st.info(guidance.get(exercise_type, "Follow the exercise instructions while recording."))
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

    st.markdown("**Record your attempt**")
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

    # Recorded audio playback
    recorded = st.session_state.get("recorded_audio")
    rec_duration = None
    if recorded:
        st.markdown("**Your recording**")
        st.audio(recorded, format="audio/wav")
        rec_duration = _recording_duration_seconds(recorded)

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
        items_html = ""
        for item in feedback_list:
            if isinstance(item, dict):
                time_code = item.get("time", "")
                message   = item.get("message", "")
                items_html += f"""
                <div class="feedback-item">
                    <span class="feedback-timestamp">{time_code}</span>
                    <span class="feedback-text">{message}</span>
                </div>"""
            else:
                items_html += f'<div class="feedback-item"><span class="feedback-text">{item}</span></div>'
        st.markdown(items_html, unsafe_allow_html=True)

    st.divider()

    # Coaching summary
    from engine.coaching import generate_coaching_summary
    summary       = generate_coaching_summary(score, feedback_list, subscores)
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
