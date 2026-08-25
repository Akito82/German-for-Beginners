# pages/01_vocabulary.py
import streamlit as st
import json
import os
from gtts import gTTS
import tempfile

st.set_page_config(
    page_title="📖 Vocabulary - German Learning",
    page_icon="📖",
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

# ---------- HEADER ----------
st.title("📖 Vocabulary Search")
st.markdown("Search for German words and save them to your collection")

# ---------- SEARCH ----------
col1, col2 = st.columns([3, 1])
with col1:
    search_term = st.text_input("🔍 Search for a German word:", placeholder="e.g., Haus, gehen, etc.")
with col2:
    st.write("")
    st.write("")
    level_filter = st.selectbox("Level", ["All", "A1", "A2", "B1"])

# ---------- SEARCH RESULTS ----------
if search_term:
    search_lower = search_term.lower().strip()
    results = []
    
    for word in st.session_state.vocabulary:
        german = word.get('german', '').lower()
        english = word.get('english', '').lower()
        german_raw = word.get('german_raw', '').lower()
        
        if (search_lower in german or 
            search_lower in english or 
            search_lower in german_raw):
            
            level = word.get('source_deck', '')
            if level_filter == "All" or level == level_filter:
                results.append(word)
    
    st.write(f"Found **{len(results)}** result(s)")
    
    for i, word in enumerate(results):
        with st.container(border=True):
            german_raw = word.get('german_raw', '').strip()
            german = word.get('german', '').strip()
            english = word.get('english', '').strip()
            example = word.get('example', '').strip()
            plural = word.get('plural', '').strip()
            level = word.get('source_deck', 'Unknown')
            
            article_colors = {'der': '#3498db', 'die': '#e74c3c', 'das': '#2ecc71'}
            color = article_colors.get(german_raw.lower(), '#2c3e50')
            display = f"{german_raw} {german}" if german_raw else german
            
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"<span style='font-size:1.3rem;font-weight:bold;color:{color};'>{display}</span>", unsafe_allow_html=True)
                if plural:
                    st.caption(f"📚 Plural: {plural}")
                st.caption(f"🇬🇧 {english}")
                if example:
                    st.caption(f"💬 {example}")
                st.caption(f"📦 {level}")
            with col2:
                if st.button(f"🔊", key=f"speak_{i}"):
                    text_to_speech(f"{german_raw} {german}" if german_raw else german)
            with col3:
                if st.button(f"💾 Save", key=f"save_{i}"):
                    if german not in [w.get('german', '') for w in st.session_state.my_words]:
                        st.session_state.my_words.append({
                            'german': german,
                            'english': english,
                            'example': example,
                            'german_raw': german_raw,
                            'plural': plural
                        })
                        st.success(f"✅ Saved '{german}'")
                    else:
                        st.warning("Already saved!")
else:
    st.info("🔍 Enter a search term to find German words")
