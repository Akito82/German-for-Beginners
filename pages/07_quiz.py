# pages/07_quiz.py - Supports both old and new quiz formats
import streamlit as st
import json
import os
import random

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="❓ Quiz - German Learning",
    page_icon="❓",
    layout="wide"
)

# ---------- DEFAULT QUESTIONS ----------
DEFAULT_QUESTIONS = [
    {"question": "What is the German word for 'house'?", "right": "das Haus", "wrong": ["der Haus", "die Haus"]},
    {"question": "What is the German word for 'car'?", "right": "das Auto", "wrong": ["der Auto", "die Auto"]},
]

@st.cache_data
def load_questions():
    try:
        if os.path.exists("data/quiz.json"):
            with open("data/quiz.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    # Convert to consistent format
                    converted = []
                    for q in data:
                        if isinstance(q, dict):
                            # Check if it's old format (wrong and wrong2 as strings)
                            if 'wrong' in q and 'wrong2' in q and isinstance(q['wrong'], str):
                                converted.append({
                                    "question": q.get('question', ''),
                                    "right": q.get('right', ''),
                                    "wrong": [q.get('wrong', ''), q.get('wrong2', '')]
                                })
                            elif 'wrong' in q and isinstance(q['wrong'], list):
                                # Already in new format
                                converted.append(q)
                            else:
                                # Fallback - try to extract what we can
                                wrong_list = []
                                if 'wrong' in q:
                                    if isinstance(q['wrong'], list):
                                        wrong_list = q['wrong']
                                    else:
                                        wrong_list.append(str(q['wrong']))
                                if 'wrong2' in q and q['wrong2'] not in wrong_list:
                                    wrong_list.append(str(q['wrong2']))
                                
                                converted.append({
                                    "question": q.get('question', ''),
                                    "right": q.get('right', ''),
                                    "wrong": wrong_list[:2]  # Take first 2
                                })
                    return converted
    except Exception as e:
        print(f"Error loading quiz: {e}")
    return DEFAULT_QUESTIONS

# ---------- SESSION STATE ----------
def init_state():
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = load_questions()
    
    if 'q_current_question' not in st.session_state:
        st.session_state.q_current_question = None
    if 'q_options' not in st.session_state:
        st.session_state.q_options = []
    if 'q_score' not in st.session_state:
        st.session_state.q_score = 0
    if 'q_total' not in st.session_state:
        st.session_state.q_total = 0
    if 'q_answered' not in st.session_state:
        st.session_state.q_answered = False
    if 'q_selected_answer' not in st.session_state:
        st.session_state.q_selected_answer = None
    if 'q_feedback' not in st.session_state:
        st.session_state.q_feedback = ""
    if 'q_feedback_type' not in st.session_state:
        st.session_state.q_feedback_type = "info"
    if 'q_correct_count' not in st.session_state:
        st.session_state.q_correct_count = 0
    if 'q_streak' not in st.session_state:
        st.session_state.q_streak = 0

init_state()

# ---------- FUNCTIONS ----------
def load_new_question():
    questions = st.session_state.quiz_questions
    if not questions:
        st.session_state.q_feedback = "No questions available!"
        st.session_state.q_feedback_type = "error"
        return
    
    question = random.choice(questions)
    st.session_state.q_current_question = question
    
    # Build options from the question data
    right = question.get('right', '')
    wrong_list = question.get('wrong', [])
    
    # If wrong is a string, convert to list
    if isinstance(wrong_list, str):
        wrong_list = [wrong_list]
    
    # Ensure we have at least 2 wrong answers, pad if needed
    while len(wrong_list) < 2:
        wrong_list.append(f"Unknown {len(wrong_list) + 1}")
    
    # Take first 2 wrong answers
    wrong_list = wrong_list[:2]
    
    options = [right] + wrong_list
    random.shuffle(options)
    st.session_state.q_options = options
    st.session_state.q_answered = False
    st.session_state.q_selected_answer = None
    st.session_state.q_feedback = ""
    st.session_state.q_feedback_type = "info"

def check_answer(selected):
    question = st.session_state.q_current_question
    if not question:
        return
    
    st.session_state.q_answered = True
    st.session_state.q_selected_answer = selected
    st.session_state.q_total += 1
    
    if selected == question['right']:
        st.session_state.q_score += 10
        st.session_state.q_correct_count += 1
        st.session_state.q_streak += 1
        st.session_state.q_feedback = f"✅ Correct! +10 points! (Streak: {st.session_state.q_streak})"
        st.session_state.q_feedback_type = "success"
    else:
        st.session_state.q_streak = 0
        st.session_state.q_feedback = f"❌ Wrong! The answer was: {question['right']}"
        st.session_state.q_feedback_type = "error"

# ---------- UI ----------
st.title("🧠 Deutsch-Quiz")
st.markdown("Test your German knowledge with multiple choice questions!")

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⭐ Score", st.session_state.q_score)
with col2:
    accuracy = (st.session_state.q_correct_count / st.session_state.q_total * 100) if st.session_state.q_total > 0 else 0
    st.metric("📊 Accuracy", f"{accuracy:.0f}%")
with col3:
    st.metric("📝 Questions", st.session_state.q_total)
with col4:
    st.metric("🔥 Streak", st.session_state.q_streak)

st.divider()

# Controls
if st.button("🔄 New Question", use_container_width=True, type="primary"):
    load_new_question()
    st.rerun()

st.divider()

# Load first question if none exists
if not st.session_state.q_current_question:
    load_new_question()
    if not st.session_state.q_current_question:
        st.warning("No questions loaded! Please check your data/quiz.json file.")
        st.stop()

# Display question
question = st.session_state.q_current_question
st.subheader(f"📝 Question {st.session_state.q_total + 1}")
st.markdown(f"**{question['question']}**")

st.divider()

# Options
st.subheader("Choose your answer:")

for i, option in enumerate(st.session_state.q_options):
    disabled = st.session_state.q_answered
    
    if st.session_state.q_answered:
        if option == question['right']:
            btn_type = "primary"
        elif option == st.session_state.q_selected_answer:
            btn_type = "secondary"
        else:
            btn_type = "secondary"
    else:
        btn_type = "primary"
    
    # Use a unique key for each button
    button_key = f"quiz_opt_{i}_{hash(option)}"
    
    if st.button(f"{chr(65 + i)}. {option}", key=button_key, use_container_width=True, disabled=disabled, type=btn_type):
        if not st.session_state.q_answered:
            check_answer(option)
            st.rerun()

# Feedback
if st.session_state.q_feedback:
    if st.session_state.q_feedback_type == "success":
        st.success(st.session_state.q_feedback)
    else:
        st.error(st.session_state.q_feedback)

# Next button
if st.session_state.q_answered:
    if st.button("➡️ Next Question", use_container_width=True):
        load_new_question()
        st.rerun()

st.divider()
st.caption(f"📊 Correct: {st.session_state.q_correct_count}/{st.session_state.q_total}")
