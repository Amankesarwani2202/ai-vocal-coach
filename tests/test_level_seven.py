import io
import numpy as np
import soundfile as sf
import pytest
from engine.audio_analysis import analyze_audio
from utils.audio_generator import generate_exemplar_audio
from utils.exercise_models import get_profile,note_grid
from components.course_completion import certificate,journey
from utils.pages_config import PAGES_MANIFEST
SR=16000

def wav(y):
    b=io.BytesIO();sf.write(b,y,SR,format='WAV');return b.getvalue()

def example(code):return generate_exemplar_audio(code.replace('.','_'))

@pytest.mark.parametrize('code',['7.1','7.2','7.3','7.4','7.5'])
def test_level_seven_reference_is_scored_with_real_dimensions(code):
    result=analyze_audio(wav(example(code)),code)
    assert result['complete'],result['feedback']
    assert 'Voice Presence' not in result['subscores']
    assert 'Register Connection' not in result['subscores']
    if code=='7.1':assert result['subscores']['Arrival Accuracy']>=90
    if code=='7.2':assert 'Glide Smoothness' not in result['subscores'] and 'Register Release' in result['subscores']
    if code=='7.3':
        assert set(result['subscores'])=={'Grace Note Clarity','Beat Stability','Landing Accuracy'}
        assert result['subscores']['Grace Note Clarity']>=75
    if code=='7.4':assert result['subscores']['Pitch Accuracy']>=90
    if code=='7.5':
        assert result['subscores']['Pitch Accuracy']>=90
        assert result['subscores']['Note Distinctness (Agility)']>=80
        assert result['subscores']['Tempo Progression']>=80
    assert max(result['pitch_data']['times'])<result['analysis_meta']['valid_performance_end_seconds']

@pytest.mark.parametrize('hz',[130.8128,261.6256,392,523.251])
def test_fast_run_anchor_tracks_singer_octave(hz):
    p=get_profile('7.5');bounds,offsets=note_grid(p);parts=[]
    for i,o in enumerate(offsets):
        t=np.arange(int((bounds[i+1]-bounds[i])*SR))/SR
        parts.append(.2*np.sin(2*np.pi*hz*2**(o/12)*t))
    result=analyze_audio(wav(np.concatenate(parts)),'7.5')
    assert result['subscores']['Pitch Accuracy']>=90
    assert result['pitch_data']['root_hz']==pytest.approx(hz,rel=.025)


def test_bad_target_is_withheld_instead_of_zero_score():
    r=analyze_audio(wav(example('7.5')),'7.5',{'root_hz':65.4})
    assert 'Pitch Accuracy' not in r['subscores']
    assert 'Pitch Accuracy' in r['withheld_metrics']
    assert not r['complete'] and r['xp']==0
    assert not any(e['rule']=='pitch_landing' for e in r['feedback'])


def test_no_ornament_cannot_earn_clarity():
    p=get_profile('7.3');bound,_=note_grid(p)
    t=np.arange(int(bound[-1]*SR))/SR
    r=analyze_audio(wav(.2*np.sin(2*np.pi*392*t)),'7.3')
    assert r['subscores']['Grace Note Clarity']==0
    assert any(e['rule']=='missing_grace' for e in r['feedback'])


def test_tracking_dropout_does_not_penalize_glide_connection(monkeypatch):
    import engine.exercise_analysis as engine
    y=wav(example('7.1'));base=engine.extract_features(y)
    original=engine.extract_features
    def dropped(data):
        f=original(data);mask=(f.relative_times>1.5)&(f.relative_times<1.75)
        f.voiced[mask]=False;f.f0[mask]=np.nan
        return f
    normal=analyze_audio(y,'7.1');monkeypatch.setattr(engine,'extract_features',dropped)
    result=analyze_audio(y,'7.1')
    assert result['subscores']['Pitch Connection']==normal['subscores']['Pitch Connection']
    assert result['subscores']['Continuity']==normal['subscores']['Continuity']
    assert any('excluded' in e['message'] for e in result['feedback'])


def test_capstone_has_no_external_target_or_pass_fail():
    t=np.arange(18*SR)/SR
    y=(.1+.05*np.sin(np.pi*t/18))*np.sin(2*np.pi*220*t)
    r=analyze_audio(wav(y),'7.6',{'planned_breaths':[6,12]})
    assert r['complete'] and r['reflection_only'] and r['xp']==0
    assert all(x is None for x in r['pitch_data']['target_f0'])
    assert 'Breath Planning' in r['subscores'] and 'Legato Continuity' in r['subscores']
    assert 'Diction Clarity' in r['withheld_metrics']


def test_certificate_does_not_claim_unfinished_course_and_ignores_old_scores():
    state={'completed_exercises':{'40_Exercise_7.6_Capstone_Performance'},'history':[{'exercise':'39_Exercise_7.5_Fast_Runs','subscores':{'Pitch Accuracy':0}}]}
    stats=journey(state)
    assert not stats['all_done'] and not stats['focus']
    blob=certificate('<Aman & a long name> '*8,'2026-10-17',stats)
    from PIL import Image
    assert Image.open(io.BytesIO(blob)).size==(1400,950)


def test_completion_and_free_practice_screens():
    from streamlit.testing.v1 import AppTest
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]/'ai_vocal_coach/pages'
    harness=f"""
import streamlit as st
st.navigation([st.Page({str(root/'41_Course_Completion.py')!r}),st.Page({str(root/'40_Exercise_7.6_Capstone_Performance.py')!r}),st.Page({str(root/'1_Dashboard.py')!r}),st.Page({str(root/'42_Free_Practice.py')!r})])
from components.course_completion import render_completion
render_completion()
"""
    app=AppTest.from_string(harness).run()
    assert not app.exception
    app.session_state['user_name']='Aman'
    app.session_state['completed_exercises']={k for k,v in PAGES_MANIFEST.items() if not v.get('is_dashboard')}
    app.run();assert not app.exception
    assert app.title[0].value=='You’ve completed Vocal Coach'
    app.run();assert not app.exception
    assert app.title[0].value=='Course replayed'
    free=AppTest.from_string(f"""
import streamlit as st
st.navigation([st.Page({str(root/'1_Dashboard.py')!r}),st.Page({str(root/'42_Free_Practice.py')!r})])
import runpy
runpy.run_path({str(root/'42_Free_Practice.py')!r})
""").run()
    assert not free.exception


def test_register_dropout_is_not_a_crack(monkeypatch):
    import engine.exercise_analysis as engine
    data=wav(example('7.2'));original=engine.extract_features
    normal=analyze_audio(data,'7.2')
    def dropout(data):
        f=original(data);lost=(f.relative_times>3.5)&(f.relative_times<3.7)
        f.voiced[lost]=False;f.f0[lost]=np.nan;return f
    monkeypatch.setattr(engine,'extract_features',dropout)
    result=analyze_audio(data,'7.2')
    assert result['subscores']['Register Release']==normal['subscores']['Register Release']
    assert not any(e['rule']=='register_discontinuity' for e in result['feedback'])


def test_cutoff_pitch_artifact_never_enters_score_or_chart(monkeypatch):
    import engine.exercise_analysis as engine
    data=wav(example('7.4')[:SR*7]);original=engine.extract_features
    normal=analyze_audio(data,'7.4')
    def corrupted(data):
        f=original(data);boundary=f.times>=f.end-engine.FRAME/(2*SR)
        f.f0[boundary]=70;f.voiced[boundary]=True;return f
    monkeypatch.setattr(engine,'extract_features',corrupted)
    result=analyze_audio(data,'7.4')
    assert result['subscores']==normal['subscores']
    assert 70 not in result['pitch_data']['f0']
    assert not result['complete'] and result['xp']==0


def test_fast_run_without_speedup_is_reported():
    p=get_profile('7.5');p['notes']=[dict(semitones=o,beats=1) for o in [0,2,4,2,0]*2]
    bounds,offsets=note_grid(p);parts=[]
    for i,o in enumerate(offsets):
        t=np.arange(int((bounds[i+1]-bounds[i])*SR))/SR
        parts.append(.15*np.sin(2*np.pi*261.6256*2**(o/12)*t))
    result=analyze_audio(wav(np.concatenate(parts)),'7.5')
    assert result['subscores']['Tempo Progression']<20
    assert any(e['rule']=='no_speedup' for e in result['feedback'])


def test_short_capstone_cannot_finish():
    t=np.arange(5*SR)/SR
    result=analyze_audio(wav(.2*np.sin(2*np.pi*220*t)),'7.6')
    assert not result['complete'] and result['xp']==0
