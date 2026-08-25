# pages/08_verb_trainer.py
import streamlit as st
import json
import os
import random

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="🔧 Verb Trainer - German Learning",
    page_icon="🔧",
    layout="wide"
)

# ---------- DEFAULT VERBS ----------
DEFAULT_VERBS = {
    "sein": {
        "English": "to be",
        "PRASENS": {
            "S1": ["bin"], "S2": ["bist"], "S3": ["ist"],
            "P1": ["sind"], "P2": ["seid"], "P3": ["sind"]
        },
        "PRATERITUM": {
            "S1": ["war"], "S2": ["warst"], "S3": ["war"],
            "P1": ["waren"], "P2": ["wart"], "P3": ["waren"]
        }
    },
    "haben": {
        "English": "to have",
        "PRASENS": {
            "S1": ["habe"], "S2": ["hast"], "S3": ["hat"],
            "P1": ["haben"], "P2": ["habt"], "P3": ["haben"]
        }
    },
    "gehen": {
        "English": "to go",
        "PRASENS": {
            "S1": ["gehe"], "S2": ["gehst"], "S3": ["geht"],
            "P1": ["gehen"], "P2": ["geht"], "P3": ["gehen"]
        }
    },
    "machen": {
        "English": "to do/make",
        "PRASENS": {
            "S1": ["mache"], "S2": ["machst"], "S3": ["macht"],
            "P1": ["machen"], "P2": ["macht"], "P3": ["machen"]
        }
    },
    "kommen": {
        "English": "to come",
        "PRASENS": {
            "S1": ["komme"], "S2": ["kommst"], "S3": ["kommt"],
            "P1": ["kommen"], "P2": ["kommt"], "P3": ["kommen"]
        }
    }
}

@st.cache_data
def load_verbs():
    try:
        if os.path.exists("data/german_verb_conjugations.json"):
            with open("data/german_verb_conjugations.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    return data
    except:
        pass
    return DEFAULT_VERBS

# ---------- SESSION STATE ----------
def init_state():
    if 'vt_verbs' not in st.session_state:
        st.session_state.vt_verbs = load_verbs()
    
    if 'vt_current_verb' not in st.session_state:
        st.session_state.vt_current_verb = None
    if 'vt_current_tense' not in st.session_state:
        st.session_state.vt_current_tense = None
    if 'vt_current_person' not in st.session_state:
        st.session_state.vt_current_person = None
    if 'vt_score' not in st.session_state:
        st.session_state.vt_score = 0
    if 'vt_total' not in st.session_state:
        st.session_state.vt_total = 0
    if 'vt_streak' not in st.session_state:
        st.session_state.vt_streak = 0
    if 'vt_answered' not in st.session_state:
        st.session_state.vt_answered = False
    if 'vt_feedback' not in st.session_state:
        st.session_state.vt_feedback = ""
    if 'vt_feedback_type' not in st.session_state:
        st.session_state.vt_feedback_type = "info"

init_state()

# ---------- FUNCTIONS ----------
def get_random_question():
    verbs = st.session_state.vt_verbs
    
    verb_list = [v for v in verbs.keys() if isinstance(verbs[v], dict) and "error" not in verbs[v]]
    if not verb_list:
        st.session_state.vt_feedback = "No verbs available!"
        st.session_state.vt_feedback_type = "error"
        return
    
    verb = random.choice(verb_list)
    verb_data = verbs[verb]
    
    tenses = [t for t in verb_data.keys() if t != "English" and verb_data[t] is not None]
    if not tenses:
        st.session_state.vt_feedback = f"No tenses available for {verb}!"
        st.session_state.vt_feedback_type = "error"
        return
    
    tense = random.choice(tenses)
    tense_data = verb_data[tense]
    
    persons = ["S1", "S2", "S3", "P1", "P2", "P3"]
    available_persons = [p for p in persons if p in tense_data]
    if not available_persons:
        return
    
    person = random.choice(available_persons)
    
    st.session_state.vt_current_verb = verb
    st.session_state.vt_current_tense = tense
    st.session_state.vt_current_person = person
    st.session_state.vt_answered = False
    st.session_state.vt_feedback = ""
    st.session_state.vt_feedback_type = "info"

def check_answer():
    user_answer = st.session_state.vt_input_answer.strip()
    
    if not user_answer:
        st.session_state.vt_feedback = "Please enter an answer!"
        st.session_state.vt_feedback_type = "error"
        return
    
    verb = st.session_state.vt_current_verb
    tense = st.session_state.vt_current_tense
    person = st.session_state.vt_current_person
    
    if not verb or not tense or not person:
        return
    
    correct = st.session_state.vt_verbs[verb][tense][person]
    if isinstance(correct, list):
        correct_str = " ".join(correct)
    else:
        correct_str = str(correct)
    
    st.session_state.vt_answered = True
    st.session_state.vt_total += 1
    
    if user_answer.strip().lower() == correct_str.lower():
        st.session_state.vt_score += 10
        st.session_state.vt_streak += 1
        st.session_state.vt_feedback = f"✅ Correct! +10 points! (Streak: {st.session_state.vt_streak})"
        st.session_state.vt_feedback_type = "success"
    else:
        st.session_state.vt_streak = 0
        st.session_state.vt_feedback = f"❌ Wrong! Correct: {correct_str}"
        st.session_state.vt_feedback_type = "error"

# ---------- UI ----------
st.title("🔧 Verb Conjugation Trainer")
st.markdown("Practice German verb conjugations!")

# Stats
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("⭐ Score", st.session_state.vt_score)
with col2:
    accuracy = (st.session_state.vt_score / (st.session_state.vt_total * 10) * 100) if st.session_state.vt_total > 0 else 0
    st.metric("📊 Accuracy", f"{accuracy:.0f}%")
with col3:
    st.metric("📝 Questions", st.session_state.vt_total)
with col4:
    st.metric("🔥 Streak", st.session_state.vt_streak)

st.divider()

# Controls
if st.button("🔄 New Question", use_container_width=True, type="primary"):
    get_random_question()
    st.rerun()

# Load first question if none exists
if not st.session_state.vt_current_verb:
    get_random_question()
    st.rerun()

st.divider()

# Display question
verb = st.session_state.vt_current_verb
tense = st.session_state.vt_current_tense
person = st.session_state.vt_current_person
verbs = st.session_state.vt_verbs

if verb and tense and person:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"**Verb:** {verb}")
        st.caption(f"🇬🇧 {verbs[verb].get('English', '')}")
    with col2:
        st.markdown(f"**Tense:** {tense}")
        st.markdown(f"**Person:** {person}")

st.divider()

# Answer input
if not st.session_state.vt_answered:
    user_answer = st.text_input("Enter the conjugation:", placeholder="Type your answer...", key="vt_input_answer")
    
    if st.button("📤 Check", use_container_width=True, type="primary"):
        check_answer()
        st.rerun()
else:
    # Show the answer field but disabled
    st.text_input("Enter the conjugation:", value="", placeholder="Already answered...", disabled=True)

# Feedback
if st.session_state.vt_feedback:
    if st.session_state.vt_feedback_type == "success":
        st.success(st.session_state.vt_feedback)
    else:
        st.error(st.session_state.vt_feedback)

# Next button
if st.session_state.vt_answered:
    if st.button("➡️ Next Question", use_container_width=True):
        get_random_question()
        st.rerun()

st.divider()
st.caption(f"📊 Questions answered: {st.session_state.vt_total}")
