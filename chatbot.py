import streamlit as st
import random
import json
from pathlib import Path
import time

# Configuration
NUM_FILES = 5
QUESTIONS_PER_FILE = 10
TOTAL_QUESTIONS = NUM_FILES * QUESTIONS_PER_FILE

def load_questions():
    all_questions = []
    for file_num in range(1, NUM_FILES + 1):
        path = Path(f"ccw_mcqs_{file_num}.json")
        if not path.exists():
            st.error(f"❌ Error: File ccw_mcqs_{file_num}.json not found!")
            st.stop()

        try:
            with path.open("r", encoding="utf-8") as f:
                file_questions = json.load(f)
                if len(file_questions) < 60:
                    st.error(f"File {path} has less than 60 questions!")
                    st.stop()
                selected = random.sample(file_questions, QUESTIONS_PER_FILE)
                all_questions.extend(selected)
        except json.JSONDecodeError as e:
            st.error(f"❌ JSON Error in {path}: {str(e)}")
            st.stop()
    return all_questions

def restart_quiz():
    st.session_state.questions = load_questions()
    st.session_state.q_index = 0
    st.session_state.score = 0
    st.session_state.show_feedback = False
    st.session_state.selected = None
    st.session_state.start_time = time.time()
    st.rerun()

# Initialize session state
if "questions" not in st.session_state:
    st.session_state.update({
        "questions": load_questions(),
        "q_index": 0,
        "score": 0,
        "show_feedback": False,
        "selected": None,
        "start_time": time.time()
    })

questions = st.session_state.questions
current_q = questions[st.session_state.q_index]

# --- Styling ---
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
* {{ font-family: 'Inter', sans-serif; }}
body {{
    background: url('https://img.freepik.com/free-photo/white-texture_1160-786.jpg') no-repeat center center fixed;
    background-size: cover;
}}
.stApp {{
    background-color: rgba(255, 255, 255, 0.85);
    backdrop-filter: blur(8px);
}}
.quiz-container {{ max-width: 1000px; margin: 0 auto; padding: 2rem; }}
.progress-container {{
    background: rgba(0, 0, 0, 0.1);
    border-radius: 10px;
    height: 12px;
    margin: 1.5rem 0;
    overflow: hidden;
}}
.progress-bar {{
    height: 100%;
    background: linear-gradient(90deg, #4CAF50 0%, #2E7D32 100%);
    width: {(st.session_state.q_index+1)/TOTAL_QUESTIONS*100}%;
    transition: width 0.6s ease;
}}
.question-card {{
    background: white;
    padding: 2rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
    margin: 1.5rem 0;
    animation: slideIn 0.4s ease-out;
}}
@keyframes slideIn {{
    0% {{ opacity: 0; transform: translateY(20px); }}
    100% {{ opacity: 1; transform: translateY(0); }}
}}
.option-btn {{
    width: 100%;
    padding: 1.2rem;
    margin: 0.8rem 0;
    border: 2px solid #e0e0e0;
    border-radius: 12px;
    background: white;
    text-align: left;
    transition: all 0.3s ease;
    cursor: pointer;
}}
.option-btn:hover {{
    transform: translateY(-3px);
    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.15);
    border-color: #4CAF50;
}}
.correct {{
    background: #C8E6C9 !important;
    border-color: #4CAF50 !important;
    animation: pulseCorrect 0.6s ease;
}}
.wrong {{
    background: #FFEBEE !important;
    border-color: #EF5350 !important;
    animation: pulseWrong 0.6s ease;
}}
@keyframes pulseCorrect {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.02); }}
    100% {{ transform: scale(1); }}
}}
@keyframes pulseWrong {{
    0% {{ transform: scale(1); }}
    50% {{ transform: scale(1.02); }}
    100% {{ transform: scale(1); }}
}}
.stats-card {{
    background: white;
    padding: 1.5rem;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.06);
    animation: fadeIn 0.6s ease;
}}
@keyframes fadeIn {{
    0% {{ opacity: 0; }}
    100% {{ opacity: 1; }}
}}
.quiz-title {{
    text-align: center;
    color: #2E7D32 !important;
    margin-bottom: 0.5rem !important;
}}
.subtitle {{
    text-align: center;
    color: #666;
    font-size: 0.9rem;
    margin-bottom: 2rem;
}}
</style>
""", unsafe_allow_html=True)

# --- App UI ---
elapsed_minutes = int((time.time() - st.session_state.start_time) // 60)
elapsed_seconds = int((time.time() - st.session_state.start_time) % 60)
accuracy = (st.session_state.score / (st.session_state.q_index + 1)) * 100 if st.session_state.q_index > 0 else 0

st.markdown(f"""
<div class="quiz-container">
    <h1 class="quiz-title">🤖 CCW Quizbot</h1>
    <div class="subtitle">An ELACSTA Study Group Initiative</div>
    <div class="progress-container"><div class="progress-bar"></div></div>
    <div style="text-align: center; color: #666;">
        Question {st.session_state.q_index + 1} of {TOTAL_QUESTIONS} | ⏱️ {elapsed_minutes}m {elapsed_seconds}s
    </div>
""", unsafe_allow_html=True)

# --- Question Card ---
st.markdown(f"""
<div class="question-card">
    <div style="display: flex; justify-content: space-between; align-items: start;">
        <h3 style="margin: 0; color: #333;">{current_q['question']}</h3>
        <div style="background: #4CAF50; color: white; padding: 0.5rem 1rem; border-radius: 8px;">
            ⭐ {st.session_state.score}
        </div>
    </div>
    <div style="margin-top: 1rem;">
""", unsafe_allow_html=True)

for opt_key, opt_text in current_q["options"].items():
    btn_class = "option-btn"
    if st.session_state.show_feedback:
        if opt_key == st.session_state.selected:
            btn_class += " correct" if opt_key == current_q["correct_option"] else " wrong"
        elif opt_key == current_q["correct_option"]:
            btn_class += " correct"

    if not st.session_state.show_feedback:
        if st.button(f"**{opt_key}** {opt_text}", key=f"opt-{st.session_state.q_index}-{opt_key}"):
            st.session_state.selected = opt_key
            st.session_state.show_feedback = True
            if opt_key == current_q["correct_option"]:
                st.session_state.score += 1
            st.rerun()

st.markdown("</div></div>", unsafe_allow_html=True)

# --- Feedback Section ---
if st.session_state.show_feedback:
    is_correct = st.session_state.selected == current_q['correct_option']
    st.markdown(f"""
    <div class="question-card" style="border-left: 4px solid {'#4CAF50' if is_correct else '#EF5350'};">
        <div style="display: flex; align-items: center; gap: 1rem;">
            <span style="font-size: 2rem;">{"✅" if is_correct else "❌"}</span>
            <div>
                <h3 style="margin: 0; color: {'#2E7D32' if is_correct else '#D32F2F'}">
                    {"Correct Answer!" if is_correct else "Incorrect Answer"}
                </h3>
                <p style="margin: 0.5rem 0 0; color: #666;">{current_q['explanation']}</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.session_state.q_index + 1 < TOTAL_QUESTIONS:
        if st.button("Next Question →", key="next_btn", type="primary"):
            st.session_state.q_index += 1
            st.session_state.show_feedback = False
            st.session_state.selected = None
            st.rerun()

# --- Sidebar Stats ---
st.markdown(f"""
<div class="stats-card" style="margin-top: 2rem;">
    <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; text-align: center;">
        <div>
            <div style="font-size: 1.2rem; color: #2E7D32;">{st.session_state.score}</div>
            <div style="font-size: 0.9rem; color: #666;">Correct</div>
        </div>
        <div>
            <div style="font-size: 1.2rem; color: #D32F2F;">{st.session_state.q_index - st.session_state.score + 1}</div>
            <div style="font-size: 0.9rem; color: #666;">Incorrect</div>
        </div>
        <div style="grid-column: span 2;">
            <div style="font-size: 1.2rem; color: #4CAF50;">{accuracy:.1f}%</div>
            <div style="font-size: 0.9rem; color: #666;">Accuracy</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)