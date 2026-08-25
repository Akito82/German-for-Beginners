# pages/04_hangman.py
import streamlit as st
import json
import os
import random
from gamification import gamification

st.set_page_config(
    page_title="🪢 Hangman - German Learning",
    page_icon="🪢",
    layout="wide"
)

# ---------- LOAD VOCABULARY ----------
@st.cache_data
def load_vocabulary():
    all_words = []
    files = ["data/vocabA1.json", "data/vocabA2.json", "data/vocabB1.json"]
    for file_path in files:
        if os.path.exists(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    words = json.load(f)
                    all_words.extend(words)
            except:
                pass
    return all_words

# ---------- SESSION STATE ----------
if 'vocabulary' not in st.session_state:
    st.session_state.vocabulary = load_vocabulary()
if 'my_words' not in st.session_state:
    st.session_state.my_words = []

# Initialize hangman game state
if 'hangman_word' not in st.session_state:
    if st.session_state.vocabulary:
        word_data = random.choice(st.session_state.vocabulary)
        st.session_state.hangman_word = word_data.get('german', '').lower()
        st.session_state.hangman_english = word_data.get('english', '')
        st.session_state.hangman_example = word_data.get('example', '')
    else:
        st.session_state.hangman_word = "deutsch"
        st.session_state.hangman_english = "German"
        st.session_state.hangman_example = ""

if 'hangman_guesses' not in st.session_state:
    st.session_state.hangman_guesses = []
if 'hangman_wrong' not in st.session_state:
    st.session_state.hangman_wrong = 0
if 'hangman_max_wrong' not in st.session_state:
    st.session_state.hangman_max_wrong = 6
if 'hangman_game_over' not in st.session_state:
    st.session_state.hangman_game_over = False
if 'hangman_won' not in st.session_state:
    st.session_state.hangman_won = False

# ---------- HEADER ----------
st.title("🪢 Hangman")
st.markdown("Guess the German word letter by letter!")

# ---------- GAME ----------
word = st.session_state.hangman_word
guesses = st.session_state.hangman_guesses
wrong = st.session_state.hangman_wrong
max_wrong = st.session_state.hangman_max_wrong

# Display word progress
def display_word():
    return ' '.join([letter if letter in guesses else '_' for letter in word])

if not st.session_state.hangman_game_over:
    st.markdown(f"## {display_word()}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("❌ Wrong", f"{wrong}/{max_wrong}")
    with col2:
        st.metric("✅ Correct", len([g for g in guesses if g in word]))
    with col3:
        st.metric("📝 Guessed", len(guesses))
    
    if st.session_state.hangman_english:
        st.caption(f"💡 Hint: {st.session_state.hangman_english}")
    
    # Hangman ASCII
    stages = [
        "  -----\n  |   |\n      |\n      |\n      |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n      |\n      |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n  |   |\n      |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n /|   |\n      |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n /|\\  |\n      |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n /|\\  |\n /    |\n      |\n=========",
        "  -----\n  |   |\n  O   |\n /|\\  |\n / \\  |\n      |\n========="
    ]
    st.code(stages[wrong], language="text")
    
    # Letter input
    col1, col2 = st.columns([3, 1])
    with col1:
        letter = st.text_input("Enter a letter:", max_chars=1, placeholder="Type a letter...")
    with col2:
        st.write("")
        st.write("")
        if st.button("Guess", use_container_width=True):
            if letter and len(letter) == 1:
                letter = letter.lower()
                if letter not in guesses:
                    guesses.append(letter)
                    if letter not in word:
                        wrong += 1
                        st.session_state.hangman_wrong = wrong
                    
                    if all(letter in guesses for letter in word):
                        st.session_state.hangman_won = True
                        st.session_state.hangman_game_over = True
                    elif wrong >= max_wrong:
                        st.session_state.hangman_game_over = True
                else:
                    st.warning("Already guessed!")
    
    if guesses:
        st.markdown("---")
        st.markdown("### 🔤 Guessed Letters")
        st.code(' '.join(sorted(guesses)), language="text")

else:
    if st.session_state.hangman_won:
        st.balloons()
        st.success(f"🎉 Congratulations! You guessed: **{word}**")
    else:
        st.error(f"💀 Game Over! The word was: **{word}**")
    
    if st.session_state.hangman_example:
        st.info(f"💬 Example: {st.session_state.hangman_example}")
    
    if st.button("🔄 New Game", use_container_width=True):
        if st.session_state.vocabulary:
            word_data = random.choice(st.session_state.vocabulary)
            st.session_state.hangman_word = word_data.get('german', '').lower()
            st.session_state.hangman_english = word_data.get('english', '')
            st.session_state.hangman_example = word_data.get('example', '')
        st.session_state.hangman_guesses = []
        st.session_state.hangman_wrong = 0
        st.session_state.hangman_game_over = False
        st.session_state.hangman_won = False
        st.rerun()
