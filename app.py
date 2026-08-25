# app.py - German Learning Portal (Main App)
import streamlit as st
import json
import os
import random

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="🇩🇪 German Learning Portal",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- SESSION STATE ----------
if 'vocabulary' not in st.session_state:
    st.session_state.vocabulary = []
if 'my_words' not in st.session_state:
    st.session_state.my_words = []

# ---------- LOAD DATA ----------
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

if not st.session_state.vocabulary:
    st.session_state.vocabulary = load_vocabulary()

# ---------- SIDEBAR NAVIGATION ----------
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/germany.png", width=80)
    st.title("🇩🇪 German Learning")
    st.markdown("---")
    
    # Navigation
    st.subheader("📚 Learning Tools")
    st.page_link("app.py", label="🏠 Home", icon="🏠")
    st.page_link("pages/01_vocabulary.py", label="📖 Vocabulary", icon="📖")
    st.page_link("pages/02_random_word.py", label="🎲 Random Word", icon="🎲")
    st.page_link("pages/03_my_words.py", label="💾 My Words", icon="💾")
    
    st.markdown("---")
    st.subheader("🎮 Games")
    st.page_link("pages/04_hangman.py", label="🪢 Hangman", icon="🪢")
    st.page_link("pages/05_word_builder.py", label="🔤 Word Builder", icon="🔤")
    st.page_link("pages/06_word_order.py", label="📝 Word Order", icon="📝")
    st.page_link("pages/07_quiz.py", label="❓ Quiz", icon="❓")
    
    st.markdown("---")
    st.subheader("📘 Grammar & Verbs")
    st.page_link("pages/08_verb_trainer.py", label="🔧 Verb Trainer", icon="🔧")
    #st.page_link("pages/09_grammar.py", label="📚 Grammar", icon="📚")
    st.page_link("pages/10_prefix_verb.py", label="🇩🇪 Prefix + Verb", icon="🇩🇪")

    
    st.markdown("---")
    st.caption("Made with ❤️ for German learners")
    st.caption("v2.0 • Streamlit Edition")

# ---------- HOME PAGE ----------
st.title("🇩🇪 German Learning Portal")
st.markdown("### Master German with interactive tools & games")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("📚 Words", f"{len(st.session_state.vocabulary):,}")
with col2:
    st.metric("🎮 Games", "5")
with col3:
    st.metric("📘 Levels", "A1 • A2 • B1")
with col4:
    st.metric("💾 My Words", len(st.session_state.my_words))

st.markdown("---")

# Feature grid
st.subheader("✨ Quick Start")
col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("### 📖 Vocabulary")
        st.write("Search and explore German words")
        if st.button("Go to Vocabulary", use_container_width=True):
            st.switch_page("pages/01_vocabulary.py")

with col2:
    with st.container(border=True):
        st.markdown("### 🎲 Random Word")
        st.write("Discover a new word every time")
        if st.button("Get Random Word", use_container_width=True):
            st.switch_page("pages/02_random_word.py")

with col3:
    with st.container(border=True):
        st.markdown("### 🎮 Games")
        st.write("Learn through fun games")
        if st.button("Play Games", use_container_width=True):
            st.switch_page("pages/04_hangman.py")

st.markdown("---")

# Tips
with st.expander("💡 Learning Tips"):
    st.markdown("""
    - **Daily Practice**: Spend 10-15 minutes daily
    - **Spaced Repetition**: Review words regularly
    - **Use in Context**: Try to use new words in sentences
    - **Listen & Repeat**: Use the 🔊 pronunciation feature
    - **Save & Review**: Save words to 'My Words'
    """)
