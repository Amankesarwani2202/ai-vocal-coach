import streamlit as st

def init_session_state():
    """Initializes global session state variables for progress tracking."""
    if 'xp' not in st.session_state:
        st.session_state.xp = 0
    if 'completed_exercises' not in st.session_state:
        st.session_state.completed_exercises = set()
    if 'history' not in st.session_state:
        st.session_state.history = []
    if 'best_scores' not in st.session_state:
        st.session_state.best_scores = {}

def add_score(exercise_id: str, score: int, xp_earned: int):
    """Updates user progress after an exercise."""
    st.session_state.xp += xp_earned
    st.session_state.completed_exercises.add(exercise_id)
    
    if exercise_id not in st.session_state.best_scores or score > st.session_state.best_scores[exercise_id]:
        st.session_state.best_scores[exercise_id] = score
        
    st.session_state.history.append({
        'exercise': exercise_id,
        'score': score,
        'xp': xp_earned
    })