from pathlib import Path
import sys
import pytest
from streamlit.testing.v1 import AppTest

ROOT=Path(__file__).resolve().parents[1]/'ai_vocal_coach'
sys.path.insert(0,str(ROOT/'pages'))
from utils.pages_config import PAGES_MANIFEST


@pytest.mark.parametrize('page',[name for name in PAGES_MANIFEST if not PAGES_MANIFEST[name].get('is_dashboard')])
def test_every_exercise_prepare_and_record_screen_runs(page):
    app=AppTest.from_file(str(ROOT/'pages'/(page+'.py')),default_timeout=20).run()
    assert not app.exception
    app.button(key='start_exercise').click().run()
    assert not app.exception
    assert app.session_state.exercise_stage=='recording'


def test_dashboard_ignores_retired_exercises():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=20)
    app.session_state['user_name']='Aman'
    app.session_state['completed_exercises']={'40_Exercise_8.1_Caro_Mio_Ben'}
    app.run()
    assert not app.exception
    completed=next(m for m in app.metric if m.label=='Exercises completed')
    assert completed.value=='0'


def test_incomplete_take_disables_progress_and_retry_clears_capture():
    page='30_Exercise_6.1_Forward_Placement'
    app=AppTest.from_file(str(ROOT/'pages'/(page+'.py')),default_timeout=20).run()
    app.session_state['exercise_stage']='results'
    app.session_state['exercise_analysis']={'score':20,'xp':0,'subscores':{},'feedback':[], 'complete':False}
    app.run()
    assert not app.exception
    assert app.button(key='save_score_'+page).disabled
    epoch=app.session_state.get('take_'+page,0)
    app.button(key='retry_'+page).click().run()
    assert not app.exception
    assert app.session_state.exercise_stage=='introduction'
    assert app.session_state['take_'+page]>epoch
    assert app.session_state.exercise_analysis is None
