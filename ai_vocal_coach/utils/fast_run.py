"""Require an accurate slow take before enabling the fast recording."""
from utils.exercise_models import get_profile


def phase_profile(phase):
    p=get_profile('7.5');p['run_phase']=phase
    p['notes']=p['notes'][:5] if phase=='slow' else p['notes'][5:]
    p['min_seconds']=5 if phase=='slow' else 7/3
    return p


def slow_pass_ready(result):
    return bool(result.get('complete') and result.get('subscores',{}).get('Pitch Accuracy',0)>=85 and
                result.get('subscores',{}).get('Note Distinctness (Agility)',0)>=80 and
                result.get('pitch_data',{}).get('root_hz'))
