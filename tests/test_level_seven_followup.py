import io
import json
from pathlib import Path
import numpy as np
import soundfile as sf
import pytest
from engine.audio_analysis import analyze_audio
from utils.fast_run import phase_profile,slow_pass_ready
from utils.exercise_models import note_grid,get_profile
from utils.progress_store import snapshot,validate
SR=16000


def wav(y):
    b=io.BytesIO();sf.write(b,y,SR,format='WAV');return b.getvalue()


def synth(p,shift=0,leading=0):
    bounds,offsets=note_grid(p);parts=[]
    for i,o in enumerate(offsets):
        t=np.arange(int((bounds[i+1]-bounds[i])*SR))/SR
        parts.append(.15*np.sin(2*np.pi*261.6256*2**((o+shift)/12)*t))
    return np.r_[np.zeros(int(leading*SR)),np.concatenate(parts)]


def test_slow_accuracy_gate_and_fast_phase_comparison():
    slow=phase_profile('slow');fast=phase_profile('fast')
    good=analyze_audio(wav(synth(slow)),'7.5',{'profile_overrides':slow})
    assert slow_pass_ready(good)
    wrong=dict(slow);wrong['notes']=[dict(n,semitones=0) for n in slow['notes']]
    bad=analyze_audio(wav(synth(wrong)),'7.5',{'profile_overrides':slow})
    assert not slow_pass_ready(bad)
    result=analyze_audio(wav(synth(fast)),'7.5',{'profile_overrides':fast,'slow_take':good,'root_hz':good['pitch_data']['root_hz']})
    assert result['complete']
    assert result['subscores']['Pitch Accuracy']>=90
    assert result['subscores']['Tempo Progression']>=85
    assert result['performance_duration']>=7


def test_short_slow_take_never_unlocks():
    p=phase_profile('slow')
    r=analyze_audio(wav(synth(p)[:SR*2]),'7.5',{'profile_overrides':p})
    assert not slow_pass_ready(r)


def test_ornament_count_in_clock_detects_late_main_attacks():
    p=get_profile('7.3')
    timely=analyze_audio(wav(synth(p,leading=1)),'7.3',{'performance_start_seconds':1})
    late=analyze_audio(wav(synth(p,leading=1.15)),'7.3',{'performance_start_seconds':1})
    assert timely['subscores']['Beat Stability']>late['subscores']['Beat Stability']
    assert timely['metric_evidence']['Beat Stability']['synchronized']
    assert any(e['rule']=='late_main' for e in late['feedback'])


def test_main_attacks_are_one_beat_apart():
    p=get_profile('7.3');bounds,_=note_grid(p)
    assert np.diff(bounds[1::2])==pytest.approx([60/72]*3)


def test_progress_round_trip_preserves_first_finish_without_audio():
    data=snapshot({'user_name':'Aman','xp':120,'completed_exercises':{'7.6'},'history':[],
        'course_completion_seen':True,'course_finished_at':'2026-10-17','remember_progress':True,'recorded_audio':b'private'})
    loaded=validate(json.loads(json.dumps(data)))
    assert loaded['completed_exercises']=={'7.6'}
    assert loaded['course_completion_seen'] and loaded['remember_progress']
    assert 'recorded_audio' not in data


@pytest.mark.parametrize('bad',[{'xp':float('nan')},{'history':[{'subscores':{'Pitch':float('inf')}}]}, {'completed_exercises':'7.6'}, {'course_completion_seen':True}, {'best_scores':{'7.6':'bad'}}])
def test_corrupt_progress_is_rejected(bad):
    with pytest.raises(ValueError):validate(bad)


def test_capstone_attack_proxy_and_smooth_dynamic_shape():
    t=np.arange(SR*18)/SR
    carrier=np.sin(2*np.pi*220*t)
    # Twelve syllables with short, clear entrances.
    env=np.ones(len(t))*.15
    for start in np.arange(0,18,1.5):
        a=int(start*SR);env[a:a+SR//10]=0
    diction=analyze_audio(wav(carrier*env),'7.6')
    assert 'Diction Clarity' in diction['subscores']
    flat=analyze_audio(wav(.15*carrier),'7.6')
    arc=analyze_audio(wav((.03+.12*np.sin(np.pi*t/18))*carrier),'7.6')
    assert arc['subscores']['Dynamic Shape']>flat['subscores']['Dynamic Shape']


def test_fast_run_ui_enforces_slow_gate(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import components.exercise_flow as flow
    monkeypatch.setattr(flow,'recording_input',lambda exercise,profile,reference,suffix='':(wav(synth(profile)),{}))
    root=Path(__file__).resolve().parents[1]/'ai_vocal_coach/pages/39_Exercise_7.5_Fast_Runs.py'
    app=AppTest.from_file(str(root),default_timeout=20).run()
    app.button(key='start_exercise').click().run()
    assert not app.exception
    assert 'fast_run_slow_take' not in app.session_state
    app.button(key='rec_submit').click().run()
    assert not app.exception
    assert app.session_state.exercise_stage=='recording'
    assert app.session_state.fast_run_slow_take['subscores']['Pitch Accuracy']>=85
    app.button(key='rec_submit').click().run()
    assert not app.exception
    assert app.session_state.exercise_stage=='results'
    assert app.session_state.exercise_analysis['complete']


def test_known_transition_zone_and_soft_baseline_are_used():
    p=get_profile('7.2')
    r=analyze_audio(wav(synth(p)),'7.2',{'soft_rms_baseline':.02})
    assert 'Soft Dynamic Match' in r['subscores']
    assert any(e['rule']=='too_loud' for e in r['feedback'])
    from utils.audio_generator import generate_exemplar_audio
    r=analyze_audio(wav(generate_exemplar_audio('7_1')),'7.1',{'passaggio_zone_hz':[300,350]})
    assert any(e['rule']=='known_zone_crossing' for e in r['feedback'])


def test_browser_bridge_restores_before_writing(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import components.browser_progress as storage
    saved={'user_name':'Aman','xp':55,'completed_exercises':[], 'history':[], 'remember_progress':True,
        'course_completion_seen':True,'course_finished_at':'2026-10-17'}
    calls=[]
    def bridge(**kwargs):calls.append(kwargs);return {'loaded':True,'data':saved}
    monkeypatch.setattr(storage,'_bridge',bridge)
    app=AppTest.from_string('''
from utils.state import init_session_state
from components.browser_progress import sync_browser_progress
init_session_state()
sync_browser_progress()
''').run()
    assert not app.exception
    assert app.session_state.user_name=='Aman'
    assert app.session_state.course_completion_seen
    assert not calls[0]['ready']
    assert calls[-1]['ready'] and calls[-1]['data']['xp']==55


def test_failed_slow_take_ui_stays_locked(monkeypatch):
    from streamlit.testing.v1 import AppTest
    import components.exercise_flow as flow
    p=phase_profile('slow');p['notes']=[dict(n,semitones=0) for n in p['notes']]
    monkeypatch.setattr(flow,'recording_input',lambda *a,**k:(wav(synth(p)),{}))
    root=Path(__file__).resolve().parents[1]/'ai_vocal_coach/pages/39_Exercise_7.5_Fast_Runs.py'
    app=AppTest.from_file(str(root),default_timeout=20).run()
    app.button(key='start_exercise').click().run()
    app.button(key='rec_submit').click().run()
    assert not app.exception
    assert app.button(key='save_score_39_Exercise_7.5_Fast_Runs').disabled
    assert 'fast_run_slow_take' not in app.session_state
    app.button(key='retry_39_Exercise_7.5_Fast_Runs').click().run()
    assert not app.exception
    assert 'fast_run_slow_take' not in app.session_state


def test_browser_storage_js_protocol_and_opt_out(tmp_path):
    import subprocess,os
    root=Path(__file__).resolve().parents[1]/'ai_vocal_coach/components'
    source=(root/'progress_storage/index.html').read_text().split('<script>')[1].split('</script>')[0]
    harness='''
const vm=require('vm'),assert=require('assert');
let listener,messages=[],writes=0,removes=0;
let saved=JSON.stringify({user_name:'Aman',xp:55,remember_progress:true});
const parent={postMessage:x=>messages.push(x)};
const sandbox={parent,window:{addEventListener:(type,fn)=>listener=fn},localStorage:{
 getItem:()=>saved,setItem:(k,v)=>{writes++;saved=v},removeItem:()=>{removes++;saved=null}}};
vm.runInNewContext(SOURCE,sandbox);
function render(args){listener({source:parent,data:{type:'streamlit:render',args}})}
render({ready:false,enabled:false,data:{xp:0}});
assert.equal(writes,0);assert.equal(removes,0);
assert.equal(messages.find(x=>x.type==='streamlit:setComponentValue').value.data.xp,55);
render({ready:true,enabled:true,data:{xp:65}});assert.equal(JSON.parse(saved).xp,65);
render({ready:true,enabled:false});assert.equal(saved,null);assert.equal(removes,1);
sandbox.localStorage.setItem=()=>{throw new Error('quota')};
render({ready:true,enabled:true,data:{xp:99}});
assert(messages.some(x=>x.value?.unavailable));
'''.replace('SOURCE',json.dumps(source))
    script=tmp_path/'storage-test.cjs';script.write_text(harness)
    result=subprocess.run([os.environ.get('CODEX_PRIMARY_RUNTIME_NODE','node'),str(script)],capture_output=True,text=True)
    assert result.returncode==0,result.stderr
