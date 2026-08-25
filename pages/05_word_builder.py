# pages/05_word_builder.py
import streamlit as st
import json
import os
import random
from collections import Counter
import re

# MUST BE THE FIRST STREAMLIT COMMAND
st.set_page_config(
    page_title="🔤 Word Builder - German Learning",
    page_icon="🔤",
    layout="wide"
)

# ---------- VOCABULARY LOADER ----------
@st.cache_data
def load_vocabulary():
    all_words = []
    files = ["data/vocabA1.json", "data/vocabA2.json", "data/vocabB1.json"]
    for file_path in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for entry in data:
                        if 'german' in entry:
                            all_words.append(entry)
            except:
                pass
    return all_words

# ---------- SESSION STATE ----------
def init_state():
    if 'wb_vocabulary' not in st.session_state:
        st.session_state.wb_vocabulary = load_vocabulary()
    
    if 'wb_base_word' not in st.session_state:
        st.session_state.wb_base_word = None
    if 'wb_found_words' not in st.session_state:
        st.session_state.wb_found_words = []
    if 'wb_score' not in st.session_state:
        st.session_state.wb_score = 0
    if 'wb_current_streak' not in st.session_state:
        st.session_state.wb_current_streak = 0
    if 'wb_best_streak' not in st.session_state:
        st.session_state.wb_best_streak = 0
    if 'wb_words_found' not in st.session_state:
        st.session_state.wb_words_found = 0
    if 'wb_game_started' not in st.session_state:
        st.session_state.wb_game_started = False
    if 'wb_feedback' not in st.session_state:
        st.session_state.wb_feedback = ""
    if 'wb_feedback_type' not in st.session_state:
        st.session_state.wb_feedback_type = "info"

init_state()

# ---------- GAME FUNCTIONS ----------
def get_base_word():
    vocab = st.session_state.wb_vocabulary
    long_words = [entry for entry in vocab if len(entry.get('german', '')) >= 6]
    
    if not long_words:
        fallbacks = ["arbeit", "computer", "schreiben", "deutsch", "programm", "fenster"]
        return random.choice(fallbacks)
    
    chosen = random.choice(long_words)
    return chosen['german'].lower()

def start_new_game():
    st.session_state.wb_base_word = get_base_word()
    st.session_state.wb_found_words = []
    st.session_state.wb_score = 0
    st.session_state.wb_current_streak = 0
    st.session_state.wb_best_streak = 0
    st.session_state.wb_words_found = 0
    st.session_state.wb_game_started = True
    st.session_state.wb_feedback = ""
    st.session_state.wb_feedback_type = "info"

def is_valid_subset(base_word, player_word):
    base_counts = Counter(base_word.lower())
    player_counts = Counter(player_word.lower())
    for char, count in player_counts.items():
        if base_counts[char] < count:
            return False
    return True

def is_valid_german_word(word):
    # Simple validation - accept words with German letters
    if len(word) < 2:
        return False, "Word must have at least 2 letters"
    if not re.match(r'^[a-zäöüß]+$', word):
        return False, "Only German letters allowed"
    return True, None

def check_word(word):
    word = word.strip().lower()
    
    if len(word) < 2:
        st.session_state.wb_feedback = "❌ Word must be at least 2 letters!"
        st.session_state.wb_feedback_type = "error"
        return
    
    if word in st.session_state.wb_found_words:
        st.session_state.wb_feedback = f"⚠️ '{word}' already found!"
        st.session_state.wb_feedback_type = "warning"
        return
    
    if not is_valid_subset(st.session_state.wb_base_word, word):
        st.session_state.wb_feedback = f"❌ Cannot form '{word}' from '{st.session_state.wb_base_word.upper()}'!"
        st.session_state.wb_feedback_type = "error"
        return
    
    # Valid word
    word_score = len(word)
    st.session_state.wb_score += word_score
    st.session_state.wb_found_words.append(word)
    st.session_state.wb_words_found += 1
    st.session_state.wb_current_streak += 1
    
    if st.session_state.wb_current_streak > st.session_state.wb_best_streak:
        st.session_state.wb_best_streak = st.session_state.wb_current_streak
    
    st.session_state.wb_feedback = f"✅ Correct! '{word}' (+{word_score} pts) (Streak: {st.session_state.wb_current_streak})"
    st.session_state.wb_feedback_type = "success"

# ---------- UI ----------
st.title("🔠 Wort-Baumeister")
st.markdown("Build German words from the given letters!")

# Stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("⭐ Score", st.session_state.wb_score)
with col2:
    st.metric("🔥 Streak", f"{st.session_state.wb_current_streak} (Best: {st.session_state.wb_best_streak})")
with col3:
    st.metric("📝 Words Found", st.session_state.wb_words_found)

st.divider()

# Controls
col1, col2 = st.columns(2)
with col1:
    if st.button("🔄 New Game", use_container_width=True, type="primary"):
        start_new_game()
        st.rerun()
with col2:
    if st.button("💡 Instructions", use_container_width=True):
        st.info("""
        🎯 How to Play:
        1. Form German words from the base word's letters
        2. Each letter can only be used once per word
        3. Words must be at least 2 letters long
        4. Each word gives points = number of letters
        """)

st.divider()

# Game area
if not st.session_state.wb_game_started:
    st.info("👈 Click 'New Game' to start!")
    st.stop()

# Display base word
if st.session_state.wb_base_word:
    st.markdown(f"### 📝 Letters Available:")
    st.markdown(f"<h1 style='text-align:center;color:#3498db;font-family:monospace;letter-spacing:5px;'>{st.session_state.wb_base_word.upper()}</h1>", unsafe_allow_html=True)

st.divider()

# Input
col1, col2 = st.columns([3, 1])
with col1:
    player_word = st.text_input("Enter a German word:", placeholder="Type your word...", key="wb_input")
with col2:
    st.write("")
    st.write("")
    submit = st.button("📤 Check", use_container_width=True, type="primary")

if submit and player_word:
    check_word(player_word)
    st.rerun()

# Feedback
if st.session_state.wb_feedback:
    if st.session_state.wb_feedback_type == "success":
        st.success(st.session_state.wb_feedback)
    elif st.session_state.wb_feedback_type == "warning":
        st.warning(st.session_state.wb_feedback)
    else:
        st.error(st.session_state.wb_feedback)

# Found words
st.divider()
st.subheader(f"📖 Found Words ({len(st.session_state.wb_found_words)})")

if st.session_state.wb_found_words:
    cols = st.columns(4)
    for i, word in enumerate(st.session_state.wb_found_words):
        with cols[i % 4]:
            st.markdown(f"• {word}")
else:
    st.caption("No words found yet. Start building!")
