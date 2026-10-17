"""Shared Prepare / Record / Results flow for all curriculum exercises."""

import html
import io
import wave
from pathlib import Path

import numpy as np
import streamlit as st

from utils.exercise_models import expected_seconds, get_profile

ASSET_ROOT = Path(__file__).resolve().parents[1]


def init_exercise_flow():
    for key, value in {"exercise_stage": "introduction", "exercise_recording_complete": False,
                       "current_exercise_page": None, "recorded_audio": None, "exercise_analysis": None}.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_for_new_exercise(exercise_id):
    if st.session_state.get("current_exercise_page") != exercise_id:
        reset_exercise_flow()
        st.session_state.current_exercise_page = exercise_id


def reset_exercise_flow():
    current = st.session_state.get("current_exercise_page")
    if current:
        key = f"take_{current}"
        st.session_state[key] = st.session_state.get(key, 0) + 1
    for key in ("vowel_results", "vowel_index", "spoken_audio_bytes", "dc_phase"):
        st.session_state.pop(key, None)
    for key in list(st.session_state):
        if key.startswith("vowel_result_"):
            st.session_state.pop(key, None)
    st.session_state.exercise_stage = "introduction"
    st.session_state.exercise_recording_complete = False
    st.session_state.recorded_audio = None
    st.session_state.exercise_analysis = None
    st.session_state.pop("fast_run_slow_take",None)


def move_to_recording():
    st.session_state.exercise_stage = "recording"


def move_to_results():
    st.session_state.exercise_stage = "results"
    st.session_state.exercise_recording_complete = True


def render_stage_indicator(current_stage):
    stages = [("introduction", "Prepare"), ("recording", "Record"), ("results", "Results")]
    current = next((i for i,(key,_) in enumerate(stages) if key == current_stage), 0)
    parts = []
    for i,(key,label) in enumerate(stages):
        css = "active" if i == current else "done" if i < current else ""
        parts.append(f'<span class="stage-step {css}">{label}</span>')
        if i < 2:
            parts.append('<span class="stage-sep"></span>')
    st.markdown(f'<div class="stage-bar">{"".join(parts)}</div>', unsafe_allow_html=True)


def _render_reference(exercise_info,active_profile=None):
    profile=active_profile or get_profile(exercise_info.get('title',''))
    if profile['code'].startswith('7.') and profile['code']!='7.6':
        from utils.audio_generator import generate_exemplar_audio
        st.markdown('**Listen to the reference pattern**')
        if profile.get('run_phase'):
            from utils.audio_generator import generate_profile_audio
            st.audio(generate_profile_audio(profile),sample_rate=16000)
        else:st.audio(generate_exemplar_audio(profile['code'].replace('.','_')),sample_rate=16000)
        st.caption('Synthetic pitch and timing reference; choose a comfortable key before singing.')
    exemplar = exercise_info.get("exemplar_asset")
    if exemplar and (ASSET_ROOT / exemplar).is_file():
        st.markdown("**Listen to the example**")
        st.audio((ASSET_ROOT / exemplar).read_bytes(), format="audio/wav")
        if get_profile(exercise_info.get("title", "")).get("notes"):
            st.caption("Instrumental reference for the note pattern; vocal articulation and tone may differ.")
    alternate = exercise_info.get("alternate_exemplar_asset")
    if alternate and (ASSET_ROOT / alternate).is_file():
        with st.expander("Additional supplied example"):
            st.caption(exercise_info.get("alternate_exemplar_label", "Additional example"))
            st.audio((ASSET_ROOT / alternate).read_bytes(), format="audio/wav")


def _render_score(exercise_info):
    score = exercise_info.get("score_asset")
    if score and (ASSET_ROOT / score).is_file():
        with st.expander("View the exercise score"):
            st.image(str(ASSET_ROOT / score), caption=exercise_info["title"], width="stretch")


def render_introduction_stage(exercise_info):
    title = exercise_info.get("title", "Exercise")
    code, _, name = title.partition(" ")
    st.markdown(f'<div class="exercise-hero"><div class="exercise-number">Exercise {html.escape(code)} · Level {exercise_info.get("level", "")}</div><h1>{html.escape(name or code)}</h1><p class="subtitle">{html.escape(exercise_info.get("description", ""))}</p></div>', unsafe_allow_html=True)
    st.caption(f"{exercise_info.get('difficulty', '')} · About {exercise_info.get('duration_minutes', 0)} minutes · " + " · ".join(exercise_info.get("skills", [])))
    _render_reference(exercise_info)
    _render_score(exercise_info)
    st.markdown("**How to do it**")
    for i,instruction in enumerate(exercise_info.get("instructions", []), 1):
        st.markdown(f'<div class="instruction-step"><span class="step-number">{i}</span><span class="step-text">{html.escape(instruction)}</span></div>', unsafe_allow_html=True)
    if st.button("Start exercise", key="start_exercise"):
        move_to_recording()
        st.rerun()


_FOCUS = {
    "staccato": "Part 1: leave clear silence between the notes. Part 2: connect the same notes without re-attacking.",
    "scale_ascending": "Land each step directly; keep support for the last two notes.",
    "scale_descending": "Keep the same breath energy as you descend.",
    "minor_scale": "Keep the third and seventh natural; do not follow the raised seventh in the harmonic-minor alternative.",
    "intervals": "Hear the higher note first, then make a direct leap without sliding.",
    "arpeggios": "Keep the leaps clear and the volume even; allow the tone to lighten.",
    "legato_melody": "Move by steps and swell gently toward mi, then ease back to do.",
    "legato_notes": "Only the pitch changes: keep vowel, volume, and airflow connected.",
    "breath_phrasing": "Breathe only at the end of bar 2 if needed.",
    "melodic_etude": "Breathe at the end of bar 4; shape each phrase and keep the ending supported.",
    "vocalises": "Connect the skips, swell toward sol, and hold the final do for two beats.",
    "forward_placement": "Hum, open to ah, and sustain at three comfortable pitches, about four seconds per round.",
    "resonance_colours": "Keep one comfortable pitch: three seconds bright, three balanced, then three dark.",
    "mixing_registers": "Glide up and return smoothly; changing pitch is the task.",
    "portamento": "Glide directly between the notes with a smooth rate of change.",
    "register_turning_points": "Keep the register transition connected without an abrupt push.",
    "dynamic_shaping": "Soft → controlled peak → soft, with pitch centred throughout.",
    "messa_di_voce": "Use ten seconds for a complete soft → peak → soft arc without pressing.",
    "vowel_sustain": "Hold the intended vowel for 3–4 seconds without changing the mouth shape.",
    "vowel_ascending": "Keep ah the same while moving up each scale step.",
    "vowel_modification": "Open ah subtly toward aw as you approach your own break point.",
    "consonant_clarity": "Na, Ma, La, Ra: five quick, clear repetitions of each.",
    "tongue_tension": "Keep the jaw loose: ah for five seconds, ee for five, then oo for five.",
    "diction_challenge": "Keep the consonants as defined as in your spoken recording; finish each word.",
    "metronome_singing": "TA or DA on each click for four bars; listen to the count-in first.",
    "rhythm_quarters": "TA TA TAA: one beat, one beat, two beats. Repeat four times at 80 BPM.",
    "rhythm_compound": "LA-la-la LA-la-la: group subdivisions as 3+3 and stress the first of each group.",
    "clap_sing": "Four bars of claps alone, then four bars with two quarter-note claps per half-note sung note.",
    "syncopation": "Rest on beat 1; enter on the and of 1 and hold across beat 2. Repeat four times.",
    "warm_up": "Inhale low, keep the shoulders still, then exhale gently on sss for eight seconds.",
    "breath_support": "Keep a steady, gentle sss exhalation for eight seconds.",
    "pitch_stability": "Match the reference and hold it steadily for 6–8 seconds.",
    "scale": "Follow do-re-mi-re-do in one breath, matching the supplied score and example.",
    "legato": "Connect do-re-mi without a breath or re-attack between the notes.",
}


def recording_input(exercise_id, profile=None, reference_hz=None, suffix=""):
    from components.live_recorder import live_recorder
    profile = dict(profile or get_profile(exercise_id))
    epoch = st.session_state.get(f"take_{exercise_id}", 0)
    key = f"record_{exercise_id}_{epoch}_{suffix}"
    method = st.radio("Recording mode", ["Record with live cues", "Simple microphone"], key=f"method_{exercise_id}_{suffix}", horizontal=True)
    if method == "Record with live cues":
        audio, context = live_recorder(profile, key, reference_hz)
        st.caption("If microphone access is unavailable here, select Simple microphone.")
    else:
        recording = st.audio_input("Record your attempt", key=key, sample_rate=16000)
        audio = recording.getvalue() if recording is not None else None
        context = {}
    return audio, context


def render_recording_stage(exercise_id, breathing_type="support", context=None):
    from utils.pages_config import get_page_info
    from engine.audio_analysis import analyze_audio
    profile = get_profile(exercise_id)
    info = get_page_info(exercise_id)
    context = dict(context or {})
    if profile['code']=='7.5':
        from utils.fast_run import phase_profile
        slow=st.session_state.get('fast_run_slow_take')
        phase='fast' if slow else 'slow'
        profile=phase_profile(phase)
        context['profile_overrides']=profile
        if slow:
            profile['reference_root_hz']=slow['pitch_data']['root_hz']
            context['slow_take']=slow
            context['root_hz']=slow['pitch_data']['root_hz']
            st.success(f"Slow pass confirmed: {slow['subscores']['Pitch Accuracy']}/100 pitch accuracy. Now record only the fast turn at 180 BPM, holding the final tonic for one second.")
        else:
            st.info('Phase 1: record only C–D–E–D–C at 60 BPM. The fast phase unlocks after at least 85/100 pitch accuracy and four distinct notes.')
    st.markdown("**Your pattern and focus**")
    st.info(_FOCUS.get(profile["type"], "Use the written exercise below and keep the sound comfortable."))
    if not profile["code"].startswith("7.") and (profile.get("notes") or profile["pitch_model"] == "rhythm"):
        bpm = st.slider("Tempo (BPM)", 40, 200, int(profile["bpm"]), key=f"tempo_{exercise_id}")
        profile["bpm"] = bpm
        context["bpm"] = bpm
    st.caption(f"Allow about {expected_seconds(profile):.1f} seconds for the complete performance. The breath before your first note is excluded from feedback.")
    with st.expander("Exercise instructions and reference"):
        for instruction in info.get("instructions", []):
            st.write(instruction)
        _render_reference(info,profile)
        _render_score(info)
    reference = None
    if profile['code'] in {'7.1','7.2','7.4','7.5'} and not (profile['code']=='7.5' and st.session_state.get('fast_run_slow_take')):
        key=st.selectbox('Starting pitch',['Use my first clear sung note','C3','C4','C5','G3','G4','C♯4'],key='start_pitch_'+exercise_id)
        midi={'C3':48,'C4':60,'C5':72,'G3':55,'G4':67,'C♯4':61}
        if key in midi:
            from utils.audio_generator import generate_tone
            reference=440*2**((midi[key]-69)/12)
            context['root_hz']=reference
            st.audio(generate_tone(reference,1),sample_rate=16000)
        if profile['code']=='7.2':
            st.caption('A range finder estimates range, not passaggio. Use a comfortable key; the default starts on C♯4.')
    if profile['code'] in {'7.1','7.2'}:
        if st.checkbox('Use my known register-transition zone',key='known_zone_'+exercise_id):
            st.caption('Use a zone you have identified through practice or with a teacher. Range Finder alone cannot identify it.')
            saved=st.session_state.get('voice_profile',{}).get('passaggio_zone_hz',[300.,350.])
            low=st.number_input('Transition zone low (Hz)',65.,1000.,float(saved[0]),key='zone_low_'+exercise_id)
            high=st.number_input('Transition zone high (Hz)',65.,1050.,float(saved[1]),key='zone_high_'+exercise_id)
            if low<high:
                context['passaggio_zone_hz']=[low,high]
                st.session_state.voice_profile['passaggio_zone_hz']=[low,high]
                if profile['code']=='7.2':
                    context['root_hz']=float(np.sqrt(low*high)/2**(3/12))
                    from utils.audio_generator import generate_tone
                    st.audio(generate_tone(context['root_hz'],1),sample_rate=16000)
                    st.caption(f"Pattern centred on your known transition zone; starting pitch {context['root_hz']:.0f} Hz.")
            else:st.info('The upper boundary must be above the lower boundary. The default pitch choice is used until corrected.')
    if profile['code']=='7.2':
        with st.expander('Optional soft-voice calibration'):
            st.caption('Record two seconds of a comfortable soft ah, using the same microphone position and gain as this exercise. This compares recorded level with your own baseline, not absolute vocal loudness.')
            baseline=st.audio_input('Record a soft reference',sample_rate=16000,key='soft_reference_'+exercise_id)
            if baseline:
                from engine.exercise_analysis import extract_features
                try:
                    f=extract_features(baseline.getvalue())
                    if f.duration>=1.8 and np.sum(f.voiced)>=100:
                        context['soft_rms_baseline']=float(np.median(f.rms[f.voiced]))
                        st.caption('Soft reference is ready for this take.')
                    else:st.info('Record at least two seconds of clear soft singing for calibration.')
                except (ValueError,RuntimeError):st.info('The soft reference could not be analysed. Record it again.')
    if profile['code']=='7.6':
        text=st.text_input('Planned breath times in seconds (comma separated)',placeholder='6, 12, 18',key='planned_breaths')
        try:
            values=[float(v.strip()) for v in text.split(',') if v.strip()]
            if any(not np.isfinite(v) or v<0 or v>120 for v in values):raise ValueError()
            context['planned_breaths']=values
        except ValueError:st.info('Use seconds such as 6, 12, 18. Breath planning feedback needs valid times.')
    if profile["type"] == "pitch_stability":
        from utils.audio_generator import generate_tone
        label = st.selectbox("Reference pitch", ["A4 — 440 Hz", "C4 — 262 Hz", "A3 — 220 Hz"], key=f"reference_{exercise_id}")
        reference = {"A4 — 440 Hz": 440., "C4 — 262 Hz": 261.6256, "A3 — 220 Hz": 220.}[label]
        context["reference_hz"] = reference
        st.audio(generate_tone(reference, 2), sample_rate=16000)
    if profile["pitch_model"] == "breath":
        from components.breathing_guide import render_breathing_guide
        render_breathing_guide(profile["type"])
    st.markdown("**Record your attempt**")
    audio, recorded_context = recording_input(exercise_id,profile,reference,suffix=profile.get('run_phase',''))
    context.update(recorded_context)
    comfortable = st.session_state.get("voice_profile", {})
    if comfortable.get("range_low_hz") and comfortable.get("range_high_hz"):
        context["comfortable_range_hz"] = [comfortable["range_low_hz"], comfortable["range_high_hz"]]
    if audio:
        st.audio(audio, format="audio/wav")
        if st.button("Submit recording", key="rec_submit", use_container_width=True):
            st.session_state.recorded_audio = audio
            with st.spinner("Analysing your recording…"):
                result=analyze_audio(audio,profile['type'],context)
                if profile.get('run_phase')=='slow':
                    from utils.fast_run import slow_pass_ready
                    if slow_pass_ready(result):
                        st.session_state.fast_run_slow_take=result
                        st.session_state.recorded_audio=None
                        st.rerun()
                    result['complete']=False;result['xp']=0
                    result['feedback'].append({'rule':'slow_gate','seconds':0,'time':'','timing':'Summary','valence':'neutral','message':'Repeat the complete slow pass until pitch accuracy reaches 85/100 with at least four distinct notes. Fast recording is still locked.'})
                st.session_state.exercise_analysis=result
            move_to_results()
            st.rerun()
    if st.button("Cancel", key="rec_cancel"):
        reset_exercise_flow()
        st.rerun()
    return audio


def make_pitch_target_figure(analysis):
    import plotly.graph_objects as go
    data = analysis.get("pitch_data", {})
    times = np.asarray(data.get("times", []), dtype=float)
    actual = np.asarray(data.get("f0", []), dtype=float)
    target = np.asarray(data.get("target_f0", []), dtype=float)
    if not len(times) or len(times) != len(actual) or len(times) != len(target) or not np.any(np.isfinite(target)):
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=times, y=actual, mode="lines", name="Your pitch", line=dict(color="#2563eb", width=2), connectgaps=False))
    fig.add_trace(go.Scatter(x=times, y=target, mode="lines", name="Target notes", line=dict(color="#c2410c", width=2, shape="hv"), connectgaps=False))
    deviation = np.asarray(data.get("deviation_cents", []), dtype=float)
    if len(deviation) == len(times):
        attention = np.isfinite(actual) & np.isfinite(deviation) & (np.abs(deviation) > 70)
        # Exclude the pitch tracker's short transition windows from outlier markers.
        changes = np.flatnonzero(np.abs(np.diff(target)) > 1)
        for i in changes:
            attention[np.abs(times-times[i]) < .09] = False
        if np.any(attention):
            fig.add_trace(go.Scatter(x=times[attention], y=actual[attention], mode="markers", name="Needs attention", marker=dict(color="#7e22ce",size=6,symbol="x")))
    fig.update_layout(height=290,template="plotly_white",font=dict(color="#292524"),paper_bgcolor="#faf7f1",plot_bgcolor="#faf7f1",margin=dict(l=10,r=10,t=35,b=10),xaxis=dict(title="Seconds from first note",color="#292524",gridcolor="#d6c8b9"),yaxis=dict(title="Pitch (Hz)",color="#292524",gridcolor="#d6c8b9"),legend=dict(orientation="h",y=1.15,font=dict(color="#292524")))
    return fig


def _render_pitch_target_chart(analysis, exercise_id):
    figure = make_pitch_target_figure(analysis)
    if figure:
        st.markdown("**Pitch against the written notes**")
        st.plotly_chart(figure, width="stretch", theme=None, config={"displayModeBar":False})
        st.caption("Blue: your pitch. Orange: each held target note. Purple crosses: larger deviations. " + ("The pattern is transposed to your first note; this compares relative note accuracy." if analysis.get("analysis_meta",{}).get("relative_target") else ""))


def _render_timing_chart(analysis):
    import plotly.graph_objects as go
    timing = analysis.get("timing_data")
    if not timing:
        return
    fig = go.Figure()
    actual = timing.get("onsets_sec", [])
    grid = timing.get("beat_positions", [])
    fig.add_trace(go.Scatter(x=grid,y=[0]*len(grid),mode="markers",name="Written attacks",marker=dict(color="#c2410c",size=12,symbol="line-ns")))
    fig.add_trace(go.Scatter(x=actual,y=[1]*len(actual),mode="markers",name="Your attacks",marker=dict(color="#2563eb",size=7)))
    fig.update_layout(template="plotly_white",height=210,font=dict(color="#292524"),paper_bgcolor="#faf7f1",plot_bgcolor="#faf7f1",xaxis=dict(title="Seconds from first performance onset",color="#292524"),yaxis=dict(tickvals=[0,1],ticktext=["Target","Recorded"],color="#292524"),legend=dict(orientation="h"),margin=dict(l=10,r=10,t=20,b=10))
    st.markdown("**Timing against the written attacks**")
    st.plotly_chart(fig, width="stretch", theme=None, config={"displayModeBar":False})


def render_feedback_and_summary(analysis, exercise_id):
    from engine.coaching import generate_coaching_summary
    events = analysis.get("feedback", [])
    detailed = [e for e in events if isinstance(e,dict) and e.get("timing") != "Summary"]
    if detailed:
        st.markdown("**Feedback timeline**")
        for item in sorted(detailed,key=lambda e:e.get("seconds",0)):
            label = f"{item.get('round','')} {item.get('time','')}".strip()
            st.write(f"**{label}** · {item.get('message','')}")
    summary = generate_coaching_summary(analysis.get("score",0),events,analysis.get("subscores",{}),exercise_id=exercise_id)
    st.markdown("**Coaching summary**")
    for key,label in (("what_went_well","What went well"),("work_on","Focus on next time"),("observations","Observations")):
        st.markdown(f"**{label}**")
        items = summary[key]
        if items:
            for message in items:
                st.write("· " + message)
        else:
            st.caption("No additional observations were needed for this take.")
    st.markdown("**Recommendation**")
    st.write(summary["next_time"])


def render_results_stage(exercise_id, next_page):
    from utils.state import add_score
    analysis = st.session_state.get("exercise_analysis") or {}
    score = analysis.get("score",0)
    complete = analysis.get("complete",True)
    label = "Incomplete take" if not complete else "Excellent" if score >= 85 else "Good" if score >= 70 else "Keep practising"
    reflection=analysis.get('reflection_only',False)
    if reflection:st.markdown('### Your vocal profile')
    else:st.markdown(f"### {score}/100 · {label}")
    if not reflection:st.caption(f"+{analysis.get('xp',0)} XP" + (" · Scores describe the recorded portion; record the complete attempt before saving." if not complete else ""))
    subscores = analysis.get("subscores",{})
    entries = list(subscores.items())
    for start in range(0,len(entries),3):
        columns = st.columns(min(3,len(entries)-start))
        for column,(name,value) in zip(columns,entries[start:start+3]):
            column.metric(name,f"{value}/100")
            explanation = next((e["message"] for e in analysis.get("feedback",[]) if e.get("metric")==name and e.get("timing")=="Summary"), None)
            if explanation:
                column.caption(explanation.split(". ",1)[-1])
            elif analysis.get("metric_evidence", {}).get(name, {}).get("explanation"):
                column.caption(analysis["metric_evidence"][name]["explanation"])
    recorded = st.session_state.get("recorded_audio")
    if recorded:
        st.markdown("**Your recording**")
        st.audio(recorded,format="audio/wav")
        offset = analysis.get("analysis_meta",{}).get("onset_offset_seconds",0)
        st.caption(f"The feedback clock starts at your first performance onset, {offset:.2f}s into the recording.")
    _render_pitch_target_chart(analysis,exercise_id)
    _render_timing_chart(analysis)
    st.divider()
    if reflection:
        import plotly.graph_objects as go
        if subscores:
            names=list(subscores);values=list(subscores.values())
            fig=go.Figure(go.Scatterpolar(r=values+[values[0]],theta=names+[names[0]],fill='toself'))
            fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])),showlegend=False)
            st.plotly_chart(fig,width='stretch')
        st.caption('A reflection snapshot, with no pass/fail verdict. Pauses, melody and microphone setup can affect acoustic proxies.')
        for event in analysis.get('feedback',[]):st.write(event['message'])
        st.text_area('One thing I am proud of after listening back',key='capstone_proud')
    else:render_feedback_and_summary(analysis,exercise_id)
    st.divider()
    left,right = st.columns(2)
    with left:
        if st.button("Try again",key=f"retry_{exercise_id}",use_container_width=True):
            reset_exercise_flow()
            st.rerun()
    with right:
        action = "Finish course" if reflection else "Finish" if next_page == "pages/1_Dashboard.py" else "Save and continue"
        if st.button(action,key=f"save_score_{exercise_id}",use_container_width=True,disabled=not complete or (reflection and not st.session_state.get("capstone_proud","").strip())):
            add_score(exercise_id,score,analysis.get("xp",0),analysis=analysis)
            reset_exercise_flow()
            st.toast("Progress saved")
            st.switch_page(next_page)
    if st.button("View progress",key=f"progress_{exercise_id}"):
        st.switch_page("pages/1_Dashboard.py")


def _recording_duration_seconds(audio_bytes):
    try:
        with wave.open(io.BytesIO(audio_bytes),'rb') as recording:
            return recording.getnframes()/recording.getframerate()
    except (wave.Error,EOFError):
        return None
