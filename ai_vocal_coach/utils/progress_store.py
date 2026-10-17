"""Portable progress schema; never persist audio or recorder state."""
import math

KEYS=('user_name','xp','completed_exercises','best_scores','history','session_started_at',
      'course_finished_at','course_completion_seen','voice_profile','remember_progress')


def snapshot(state):
    return {k:sorted(state[k]) if isinstance(state.get(k),set) else state[k] for k in KEYS if k in state}


def validate(data):
    if not isinstance(data,dict):raise ValueError('Invalid progress object')
    result={k:v for k,v in data.items() if k in KEYS}
    def number(v):return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
    if not isinstance(result.get('user_name',''),str):raise ValueError('Invalid name')
    if not number(result.get('xp',0)) or result.get('xp',0)<0:raise ValueError('Invalid XP')
    done=result.get('completed_exercises',[])
    if not isinstance(done,list) or not all(isinstance(v,str) for v in done):raise ValueError('Invalid exercises')
    for key in ('best_scores','voice_profile'):
        if not isinstance(result.get(key,{}),dict):raise ValueError('Invalid profile')
    if not all(isinstance(k,str) and number(v) and 0<=v<=100 for k,v in result.get('best_scores',{}).items()):raise ValueError('Invalid scores')
    for key in ('course_completion_seen','remember_progress'):
        if key in result and not isinstance(result[key],bool):raise ValueError('Invalid flag')
    for key in ('session_started_at','course_finished_at'):
        if key in result and not isinstance(result[key],str):raise ValueError('Invalid date')
    if result.get('course_completion_seen') and not result.get('course_finished_at'):raise ValueError('Missing completion date')
    history=result.get('history',[])
    if not isinstance(history,list):raise ValueError('Invalid history')
    for row in history:
        if not isinstance(row,dict) or not isinstance(row.get('exercise',''),str):raise ValueError('Invalid history row')
        if not number(row.get('practice_seconds',0)) or row.get('practice_seconds',0)<0:raise ValueError('Invalid duration')
        scores=row.get('subscores',{})
        if not isinstance(scores,dict) or not all(isinstance(k,str) and number(v) and 0<=v<=100 for k,v in scores.items()):raise ValueError('Invalid metric')
    result['completed_exercises']=set(done)
    return result
