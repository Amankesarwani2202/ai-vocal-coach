"""Course finish, portable progress, certificate and unscored practice."""
import io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
import json
from datetime import datetime
from collections import defaultdict
import streamlit as st
from utils.pages_config import PAGES_MANIFEST


def journey(state):
    active={k for k,v in PAGES_MANIFEST.items() if not v.get('is_dashboard')}
    done=set(state.get('completed_exercises',[]))&active
    metrics=defaultdict(list)
    history=[v for v in state.get('history',[]) if v.get('exercise') in active]
    for row in history:
        if row.get('scoring_version')!='level7-v2':continue
        for name,value in row.get('subscores',{}).items():metrics[name].append(value)
    averages=sorted([(k,sum(v)/len(v)) for k,v in metrics.items() if len(v)>=2],key=lambda x:x[1],reverse=True)
    return dict(completed=len(done),total=len(active),xp=state.get('xp',0),seconds=sum(v.get('practice_seconds',0) for v in history),strengths=[k for k,v in averages if v>=80][:3],focus=[k for k,v in reversed(averages) if v<70][:2],all_done=active<=done)


def certificate(name,date,stats):
    from PIL import Image, ImageDraw, ImageFont
    image=Image.new('RGB',(1400,950),'#faf7f1');draw=ImageDraw.Draw(image)
    def font(size):
        try:return ImageFont.truetype('DejaVuSans.ttf',size)
        except OSError:return ImageFont.load_default()
    draw.rectangle((35,35,1365,915),outline='#142b42',width=5)
    def line(text,y,size=30,color='#142b42'):
        draw.text((700,y),text,fill=color,font=font(size),anchor='mt')
    line('VOCAL COACH',100,38);line('Certificate of Completion',200,54,color='#a44e30')
    # Shrink long names to keep user text within the border.
    name=(name or 'Guest').strip()[:100];size=54
    while draw.textbbox((0,0),name,font=font(size))[2]>1200 and size>16:size-=2
    line(name,330,size)
    line('has completed the Vocal Coach course' if stats['all_done'] else 'has completed the Capstone Performance',445,30)
    line(f"{stats['completed']} of {stats['total']} exercises completed",510,28)
    line(f"Recorded practice: {stats['seconds']/60:.1f} minutes",565,26)
    line(date,685,28);line('Keep singing. Keep growing.',790,25,color='#a44e30')
    output=io.BytesIO();image.save(output,format='PNG');return output.getvalue()


def progress_tools():
    from utils.progress_store import snapshot,validate
    def remember_changed():st.session_state.remember_progress=st.session_state['_remember_widget']
    if st.session_state.get('_remember_widget')!=st.session_state.get('remember_progress',False):
        st.session_state['_remember_widget']=st.session_state.get('remember_progress',False)
    st.checkbox('Remember my progress on this browser',key='_remember_widget',on_change=remember_changed)
    st.caption('Optional browser storage keeps your name, scores, reflection and first-completion record across refreshes and app reboots. Audio is never saved. Shared browsers share this profile; use a backup to move to another device.')
    if st.session_state.get('_browser_progress_unavailable'):st.info('Browser storage is unavailable here. Download a progress backup instead.')
    st.download_button('Download progress backup',json.dumps(snapshot(st.session_state)),file_name='vocal-coach-progress.json',mime='application/json',key='progress_backup')
    uploaded=st.file_uploader('Restore your progress backup',type=['json'],key='restore_progress')
    if uploaded and st.button('Restore progress'):
        try:
            if uploaded.size>2_000_000:raise ValueError('Backup is too large.')
            clean=validate(json.loads(uploaded.getvalue()))
            st.session_state.update(clean)
            st.rerun()
        except (ValueError,TypeError,KeyError):st.error('This backup could not be restored. Choose a Vocal Coach progress JSON file.')


def render_completion():
    from components.ui import inject_custom_css
    from utils.state import init_session_state
    init_session_state();inject_custom_css()
    capstone='40_Exercise_7.6_Capstone_Performance'
    if capstone not in st.session_state.completed_exercises:
        st.info('Complete the Capstone Performance to finish your journey.')
        st.page_link(str(ROOT/'pages/40_Exercise_7.6_Capstone_Performance.py'),label='Go to Capstone Performance');return
    first=not st.session_state.get('course_completion_seen',False)
    if first:
        st.session_state.course_completion_seen=True
        st.session_state.course_finished_at=datetime.now().strftime('%Y-%m-%d')
        st.balloons()
    stats=journey(st.session_state)
    st.title('You’ve completed Vocal Coach' if first and stats['all_done'] else 'Capstone complete' if first else 'Course replayed')
    if not stats['all_done']:st.info('Your capstone is complete. Revisit the remaining exercises to complete the full course.')
    a,b,c=st.columns(3);a.metric('Exercises completed',f"{stats['completed']}/{stats['total']}");b.metric('Total XP',stats['xp']);c.metric('Recorded practice',f"{stats['seconds']/60:.1f} min")
    st.write(f"Started: {st.session_state.session_started_at} · Finished: {st.session_state.course_finished_at}")
    st.caption('Practice time includes recorded attempts saved with this version; older untracked practice is not estimated.')
    if stats['strengths']:st.write('Standout strengths: '+', '.join(stats['strengths'])+'.')
    if stats['focus']:st.write('Your next focus: '+', '.join(stats['focus'])+'. Revisit these skills whenever you like.')
    if not stats['strengths'] and not stats['focus']:st.write('Keep building your profile by revisiting exercises. Strengths need repeated, verified measurements.')
    blob=certificate(st.session_state.user_name,st.session_state.course_finished_at,stats)
    st.image(blob);st.download_button('Download certificate to keep or share',blob,'vocal-coach-certificate.png','image/png')
    with st.expander('Keep your progress'):progress_tools()
    st.page_link(str(ROOT/'pages/1_Dashboard.py'),label='Revisit any exercise')
    st.page_link(str(ROOT/'pages/42_Free_Practice.py'),label='Enter free practice')
