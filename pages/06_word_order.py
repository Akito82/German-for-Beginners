# pages/06_word_order.py
import streamlit as st
import json
import os
import random

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="📝 Word Order - German Learning",
    page_icon="📝",
    layout="wide"
)

# ---------- SENTENCE DATA ----------
DEFAULT_SENTENCES = [
    {"english_translation": "The cat is sitting on the chair.", "german_sentence": "Die Katze sitzt auf dem Stuhl."},
    {"english_translation": "I am learning German.", "german_sentence": "Ich lerne Deutsch."},
    {"english_translation": "We are going to the cinema.", "german_sentence": "Wir gehen ins Kino."},
    {"english_translation": "He reads a book.", "german_sentence": "Er liest ein Buch."},
    {"english_translation": "She drinks coffee.", "german_sentence": "Sie trinkt Kaffee."},
    {"english_translation": "The children are playing in the garden.", "german_sentence": "Die Kinder spielen im Garten."},
]

@st.cache_data
def load_sentences():
    try:
        if os.path.exists("data/word_order.json"):
            with open("data/word_order.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    return data
    except:
        pass
    return DEFAULT_SENTENCES

# ---------- SESSION STATE ----------
def init_state():
    if 'wo_sentences' not in st.session_state:
        st.session_state.wo_sentences = load_sentences()
    
    if 'wo_current_sentence' not in st.session_state:
        st.session_state.wo_current_sentence = None
    if 'wo_scrambled_words' not in st.session_state:
        st.session_state.wo_scrambled_words = []
    if 'wo_selected_indices' not in st.session_state:
        st.session_state.wo_selected_indices = []
    if 'wo_selected_words' not in st.session_state:
        st.session_state.wo_selected_words = []
    if 'wo_score' not in st.session_state:
        st.session_state.wo_score = 0
    if 'wo_attempts' not in st.session_state:
        st.session_state.wo_attempts = 0
    if 'wo_solved_count' not in st.session_state:
        st.session_state.wo_solved_count = 0
    if 'wo_current_streak' not in st.session_state:
        st.session_state.wo_current_streak = 0
    if 'wo_best_streak' not in st.session_state:
        st.session_state.wo_best_streak = 0
    if 'wo_game_started' not in st.session_state:
        st.session_state.wo_game_started = False
    if 'wo_feedback' not in st.session_state:
        st.session_state.wo_feedback = ""
    if 'wo_feedback_type' not in st.session_state:
        st.session_state.wo_feedback_type = "info"
    if 'wo_answered' not in st.session_state:
        st.session_state.wo_answered = False

init_state()

# ---------- FUNCTIONS ----------
def start_new_round():
    sentences = st.session_state.wo_sentences
    if not sentences:
        st.session_state.wo_feedback = "No sentences available!"
        st.session_state.wo_feedback_type = "error"
        return
    
    sentence = random.choice(sentences)
    st.session_state.wo_current_sentence = sentence
    words = sentence['german_sentence'].split()
    random.shuffle(words)
    st.session_state.wo_scrambled_words = words
    st.session_state.wo_selected_indices = []
    st.session_state.wo_selected_words = []
    st.session_state.wo_feedback = ""
    st.session_state.wo_feedback_type = "info"
    st.session_state.wo_game_started = True
    st.session_state.wo_answered = False

def word_click(index):
    if st.session_state.wo_answered:
        return
    
    indices = st.session_state.wo_selected_indices
    words = st.session_state.wo_scrambled_words
    
    if index in indices:
        indices.remove(index)
    else:
        indices.append(index)
    
    st.session_state.wo_selected_words = [words[i] for i in indices]

def check_solution():
    if not st.session_state.wo_current_sentence or not st.session_state.wo_selected_words:
        st.session_state.wo_feedback = "Please select some words first!"
        st.session_state.wo_feedback_type = "error"
        return
    
    user_sentence = ' '.join(st.session_state.wo_selected_words)
    correct = st.session_state.wo_current_sentence['german_sentence']
    
    st.session_state.wo_attempts += 1
    st.session_state.wo_answered = True
    
    if user_sentence == correct:
        st.session_state.wo_score += 10
        st.session_state.wo_solved_count += 1
        st.session_state.wo_current_streak += 1
        if st.session_state.wo_current_streak > st.session_state.wo_best_streak:
            st.session_state.wo_best_streak = st.session_state.wo_current_streak
        st.session_state.wo_feedback = f"✅ Correct! +10 points! (Streak: {st.session_state.wo_current_streak})"
        st.session_state.wo_feedback_type = "success"
    else:
        st.session_state.wo_current_streak = 0
        st.session_state.wo_feedback = f"❌ Wrong! Correct: {correct}"
        st.session_state.wo_feedback_type = "error"

def show_solution():
    if st.session_state.wo_current_sentence:
        st.session_state.wo_feedback = f"💡 Solution: {st.session_state.wo_current_sentence['german_sentence']}"
        st.session_state.wo_feedback_type = "info"

def clear_selection():
    st.session_state.wo_selected_indices = []
    st.session_state.wo_selected_words = []
    st.session_state.wo_feedback = ""
    st.session_state.wo_feedback_type = "info"

def remove_last():
    if st.session_state.wo_selected_indices:
        st.session_state.wo_selected_indices.pop()
        words = st.session_state.wo_scrambled_words
        st.session_state.wo_selected_words = [words[i] for i in st.session_state.wo_selected_indices]

# ---------- UI ----------
st.title("🔤 Wort-Reihenfolge")
st.markdown("Put the German words in the correct order!")

# Stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⭐ Score", st.session_state.wo_score)
with col2:
    st.metric("📊 Attempts", st.session_state.wo_attempts)
with col3:
    st.metric("🔥 Streak", f"{st.session_state.wo_current_streak} (Best: {st.session_state.wo_best_streak})")

st.divider()

# Controls
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    if st.button("🔄 New Sentence", use_container_width=True, type="primary"):
        start_new_round()
        st.rerun()
with col2:
    if st.button("📤 Check", use_container_width=True):
        check_solution()
        st.rerun()
with col3:
    if st.button("💡 Show Solution", use_container_width=True):
        show_solution()
        st.rerun()
with col4:
    if st.button("🗑️ Clear", use_container_width=True):
        clear_selection()
        st.rerun()
with col5:
    if st.button("↩️ Undo", use_container_width=True):
        remove_last()
        st.rerun()

st.divider()

# Start game if not started
if not st.session_state.wo_game_started:
    st.info("👈 Click 'New Sentence' to start!")
    if st.button("Start Game", use_container_width=True):
        start_new_round()
        st.rerun()
    st.stop()

# Display game
if st.session_state.wo_current_sentence:
    st.subheader("📖 English Sentence")
    st.markdown(f"**{st.session_state.wo_current_sentence.get('english_translation', '')}**")

st.divider()

# Scrambled words
st.subheader("🔀 Scrambled Words")
if st.session_state.wo_scrambled_words:
    words = st.session_state.wo_scrambled_words
    cols = st.columns(5)
    for i, word in enumerate(words):
        with cols[i % 5]:
            is_selected = i in st.session_state.wo_selected_indices
            if is_selected:
                pos = st.session_state.wo_selected_indices.index(i) + 1
                btn_text = f"{word} ({pos})"
                btn_type = "primary"
            else:
                btn_text = word
                btn_type = "secondary"
            
            if st.button(btn_text, key=f"wo_word_{i}", use_container_width=True, type=btn_type):
                word_click(i)
                st.rerun()

# Selected words
st.divider()
st.subheader("📝 Your Sentence")
if st.session_state.wo_selected_words:
    st.markdown(f"**{ ' '.join(st.session_state.wo_selected_words) }**")
else:
    st.caption("Click words above to build your sentence...")

# Feedback
if st.session_state.wo_feedback:
    if st.session_state.wo_feedback_type == "success":
        st.success(st.session_state.wo_feedback)
    elif st.session_state.wo_feedback_type == "error":
        st.error(st.session_state.wo_feedback)
    else:
        st.info(st.session_state.wo_feedback)

# Next button after answering
if st.session_state.wo_answered:
    if st.button("➡️ Next Sentence", use_container_width=True):
        start_new_round()
        st.rerun()

st.divider()
st.caption(f"📊 Solved: {st.session_state.wo_solved_count} sentences")
