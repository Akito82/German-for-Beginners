# pages/02_random_word.py
import streamlit as st
import json
import os
import random
from gtts import gTTS
import tempfile

st.set_page_config(
    page_title="🎲 Random Word - German Learning",
    page_icon="🎲",
    layout="wide"
)

# ---------- TTS FUNCTION ----------
def text_to_speech(text, lang='de'):
    if not text or not text.strip():
        return
    try:
        tts = gTTS(text=text, lang=lang, slow=False)
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
            tts.save(fp.name)
            audio_file = open(fp.name, 'rb')
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/mpeg')
            audio_file.close()
    except Exception as e:
        st.error(f"TTS Error: {e}")

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
if 'random_word' not in st.session_state:
    st.session_state.random_word = None

# ---------- HEADER ----------
st.title("🎲 Random German Word")
st.markdown("Discover a new German word every time!")

# ---------- GENERATE RANDOM WORD ----------
col1, col2 = st.columns([2, 1])
with col2:
    with_example = st.checkbox("Only words with examples")
    if st.button("🎲 New Random Word", use_container_width=True):
        words = st.session_state.vocabulary
        if with_example:
            words_with_examples = [w for w in words if w.get('example', '').strip()]
            if words_with_examples:
                st.session_state.random_word = random.choice(words_with_examples)
            else:
                st.warning("No words with examples found")
                st.session_state.random_word = random.choice(words) if words else None
        else:
            st.session_state.random_word = random.choice(words) if words else None

# ---------- DISPLAY WORD ----------
if st.session_state.random_word:
    word = st.session_state.random_word
    
    german_raw = word.get('german_raw', '').strip()
    german = word.get('german', '').strip()
    english = word.get('english', '').strip()
    example = word.get('example', '').strip()
    plural = word.get('plural', '').strip()
    level = word.get('source_deck', 'Unknown')
    
    article_colors = {'der': '#3498db', 'die': '#e74c3c', 'das': '#2ecc71'}
    color = article_colors.get(german_raw.lower(), '#2c3e50')
    display = f"{german_raw} {german}" if german_raw else german
    
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        with col1:
            st.markdown(f"<h1 style='color:{color};'>{display}</h1>", unsafe_allow_html=True)
            if plural:
                st.markdown(f"**📚 Plural:** {plural}")
            st.markdown(f"**🇬🇧 {english}**")
            if example:
                st.markdown(f"💬 *{example}*")
            st.markdown(f"📦 **Level:** {level}")
        with col2:
            if st.button("🔊 Play", use_container_width=True):
                text_to_speech(f"{german_raw} {german}" if german_raw else german)
            if example and st.button("🔊 Example", use_container_width=True):
                text_to_speech(example)
            if st.button("💾 Save", use_container_width=True):
                if german not in [w.get('german', '') for w in st.session_state.my_words]:
                    st.session_state.my_words.append({
                        'german': german,
                        'english': english,
                        'example': example,
                        'german_raw': german_raw,
                        'plural': plural
                    })
                    st.success(f"✅ Saved!")
                else:
                    st.warning("Already saved!")
else:
    st.info("Click 'New Random Word' to start")
