import io
from pathlib import Path
import numpy as np
import pytest
import soundfile as sf
from scipy.signal import iirpeak, lfilter, sawtooth

from engine.audio_analysis import analyze_audio
from engine.exercise_analysis import extract_features, formant_track
from engine.coaching import generate_coaching_summary
from utils.exercise_models import get_profile, note_grid, beat_grid
from utils.pages_config import PAGES_MANIFEST, get_level_progress
from components.exercise_flow import make_pitch_target_figure

SR = 16000


def wav(y):
    buffer=io.BytesIO();sf.write(buffer,np.asarray(y),SR,format='WAV');return buffer.getvalue()


def tone(hz,seconds,volume=.15):
    t=np.arange(int(seconds*SR))/SR
    return np.sin(2*np.pi*hz*t)*volume


def pattern(code, leading=0, trailing=0, break_legato=False, connected_staccato=False):
    profile=get_profile(code)
    bounds, offsets=note_grid(profile)
    parts=[]
    for i,offset in enumerate(offsets):
        segment=tone(261.625565*2**(offset/12),bounds[i+1]-bounds[i])
        if code=='1.6' and i<5 and not connected_staccato:
            segment[int(len(segment)*.5):]=0
        if code=='1.6' and i>=5 and break_legato:
            segment[int(len(segment)*.6):]=0
        parts.append(segment)
    return np.r_[np.zeros(int(leading*SR)),*parts,np.zeros(int(trailing*SR))]


def rhythm(code, leading=1, shift=0, short=False):
    p=get_profile(code);grid,durations=beat_grid(p)
    length=leading+p['total_beats']*60/p['bpm']+.2
    y=np.zeros(int(length*SR))
    for i,(onset,duration) in enumerate(zip(grid,durations)):
        duration*=.45 if short else .96
        note=tone(220,duration,.15 if code!='5.3' or i%3==0 else .09)
        fade=min(160,len(note)//4)
        note[:fade]*=np.linspace(0,1,fade);note[-fade:]*=np.linspace(1,0,fade)
        start=int((leading+onset+shift)*SR)
        y[start:start+len(note)]+=note[:min(len(note),len(y)-start)]
    return y


def vowel(f1,f2,seconds=3.5):
    t=np.arange(int(SR*seconds))/SR
    y=sawtooth(2*np.pi*140*t,width=.85)
    for frequency,width in [(f1,80),(f2,100),(2800,160)]:
        b,a=iirpeak(frequency,frequency/width,fs=SR);y=lfilter(b,a,y)
    return .15*y/max(np.max(np.abs(y)),1e-9)


def test_breath_before_scale_is_not_scored_or_plotted():
    normal=analyze_audio(wav(pattern('2.1')),'2.1')
    delayed=analyze_audio(wav(pattern('2.1',leading=2,trailing=2)),'2.1')
    assert delayed['analysis_meta']['onset_offset_seconds'] == pytest.approx(2,abs=.06)
    assert delayed['score']==pytest.approx(normal['score'],abs=2)
    assert delayed['pitch_data']['times'][0]==pytest.approx(0,abs=.01)
    assert not [e for e in delayed['feedback'] if e['rule']=='unplanned_gap']


@pytest.mark.parametrize('code',['1.5','2.1','2.2','4.1','4.2'])
def test_correct_pattern_has_discrete_correct_targets(code):
    result=analyze_audio(wav(pattern(code,leading=1)),code)
    assert result['subscores']['Pitch Accuracy']>=90
    target=np.array(result['pitch_data']['target_f0'],dtype=float)
    values=np.unique(np.round(target[np.isfinite(target)],1))
    _,offsets=note_grid(get_profile(code))
    assert len(values)==len(set(offsets))
    figure=make_pitch_target_figure(result)
    assert figure.data[1].line.shape=='hv'
    assert figure.layout.font.color=='#292524'
    if code=='4.2':
        assert np.nanmax(target)/np.nanmin(target)==pytest.approx(2**(4/12),rel=.002)
    if code=='2.2':
        actual=np.array(result['pitch_data']['f0'],dtype=float)
        assert target[0]/np.nanmedian(actual[:15])==pytest.approx(1,rel=.02)


def test_staccato_silence_is_correct_but_legato_silence_is_a_break():
    good=analyze_audio(wav(pattern('1.6')),'1.6')
    broken=analyze_audio(wav(pattern('1.6',break_legato=True)),'1.6')
    smooth=analyze_audio(wav(pattern('1.6',connected_staccato=True)),'1.6')
    assert good['subscores']['Contrast']>=75
    assert not [e for e in good['feedback'] if e['rule']=='legato_gap']
    assert all(e.get('section')=='legato' for e in broken['feedback'] if e['rule']=='legato_gap')
    assert broken['subscores']['Contrast']<good['subscores']['Contrast']
    assert any(e['rule']=='staccato_connected' for e in smooth['feedback'])


def test_glide_is_never_scored_as_a_held_pitch():
    t=np.arange(10*SR)/SR
    semitones=12*(1-np.abs(2*t/10-1))
    phase=np.cumsum(220*2**(semitones/12))*2*np.pi/SR
    result=analyze_audio(wav(.15*np.sin(phase)),'6.3')
    assert 'Pitch Stability' not in result['subscores']
    assert result['subscores']['Glide Smoothness']>=85
    assert not any('hold the target' in e['message'].lower() or 'drifting away from the target' in e['message'].lower() for e in result['feedback'])


def test_quiet_dynamic_arc_is_detected_and_short_take_cannot_finish():
    t=np.arange(10*SR)/SR
    arc=.015+.12*(1-np.abs(2*t/10-1))
    result=analyze_audio(wav(arc*np.sin(2*np.pi*220*t)),'6.5')
    flat=analyze_audio(wav(tone(220,10)),'6.5')
    short=analyze_audio(wav(tone(220,4)),'6.1')
    assert result['subscores']['Dynamic Control']>=85
    assert not [e for e in result['feedback'] if e['rule']=='unplanned_gap']
    assert flat['subscores']['Dynamic Control']<30
    assert not short['complete'] and short['xp']==0
    assert any(e['rule']=='ended_early' for e in short['feedback'])


@pytest.mark.parametrize('code,count',[('5.1',16),('5.2',12),('5.3',24),('5.5',4)])
def test_each_rhythm_uses_its_own_discrete_attack_grid(code,count):
    result=analyze_audio(wav(rhythm(code)),code,{'performance_start_seconds':1})
    assert len(result['timing_data']['beat_positions'])==count
    assert result['subscores']['Pattern Completion']>=85
    assert result['timing_data']['avg_deviation_ms']<60
    assert not any('Pitch Accuracy'==name or 'Pitch Stability'==name for name in result['subscores'])


def test_half_notes_cut_short_and_on_beat_syncopation_are_identified():
    short=analyze_audio(wav(rhythm('5.2',short=True)),'5.2',{'performance_start_seconds':1})
    wrong=analyze_audio(wav(rhythm('5.5',shift=-.375)),'5.5',{'performance_start_seconds':1})
    unclocked=analyze_audio(wav(rhythm('5.5')),'5.5')
    assert any(e['rule']=='short_rhythm_note' and 'two beats' in e['message'] for e in short['feedback'])
    assert any('on the beat instead of the off-beat' in e['message'] for e in wrong['feedback'])
    assert 'Off-beat Placement' not in unclocked['subscores']
    assert 'Off-beat Placement' in unclocked['withheld_metrics']


def test_lpc_tracks_vowel_change_at_constant_pitch():
    stable=vowel(750,1150)
    changed=np.r_[vowel(750,1150,1.75),vowel(300,900,1.75)]
    first=analyze_audio(wav(stable),'3.1',{'vowel':'A','reference_hz':140})
    second=analyze_audio(wav(changed),'3.1',{'vowel':'A','reference_hz':140})
    assert 'Vowel Consistency' in first['subscores']
    assert any(e['rule']=='vowel_shift' for e in second['feedback'])
    assert second['subscores']['Vowel Consistency']<first['subscores']['Vowel Consistency']


def test_explicit_valence_and_real_different_followups_include_ties():
    events=[{'message':'The note started well but is losing its centre.','valence':'negative'},
            {'message':'This note is slightly unsettled.','valence':'neutral'}]
    summary=generate_coaching_summary(50,events,{'Pitch Stability':40,'Continuity':41},exercise_id='6.4')
    assert not any('losing' in s or 'unsettled' in s for s in summary['what_went_well'])
    assert summary['weakest_metrics']==['Pitch Stability','Continuity']
    assert '2.6 Pitch Stability' in summary['next_time']
    assert '4.1 Connecting Notes' in summary['next_time']
    for page,info in PAGES_MANIFEST.items():
        if info.get('is_dashboard'):continue
        summary=generate_coaching_summary(40,[],{'Pitch Accuracy':40},exercise_id=page)
        code=info['title'].split()[0]
        assert f'Recommended follow-up: Exercise {code} ' not in summary['next_time']


def test_every_score_has_explicit_evidence_and_no_retired_levels():
    result=analyze_audio(wav(pattern('2.1')),'2.1')
    for name in result['subscores']:
        assert name in result['metric_evidence']
        assert any(e.get('metric')==name and e['timing']=='Summary' for e in result['feedback'])
    assert set(get_level_progress(set()))==set(range(8))
    root=Path(__file__).resolve().parents[1]/'ai_vocal_coach'
    for info in PAGES_MANIFEST.values():
        assert info.get('level',0)<=7
        for key in ['exemplar_asset','score_asset','alternate_exemplar_asset']:
            if info.get(key): assert (root/info[key]).is_file(),info[key]


def test_silence_does_not_earn_scores_or_progress():
    result=analyze_audio(wav(np.zeros(SR*4)),'2.1')
    assert result['score']==0 and result['xp']==0 and not result['complete']
    assert result['subscores']=={}
