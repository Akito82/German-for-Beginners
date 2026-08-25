# pages/03_my_words.py
import streamlit as st
import json
import os

st.set_page_config(
    page_title="💾 My Words - German Learning",
    page_icon="💾",
    layout="wide"
)

# ---------- MY WORDS MANAGER ----------
class MyWordsManager:
    def __init__(self, data_file="data/my_words.json"):
        self.data_file = data_file
        self.words = []
        self.load_words()
    
    def load_words(self):
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.words = json.load(f)
            else:
                self.words = []
        except:
            self.words = []
    
    def save_words(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False
    
    def add_word(self, german, english, example=""):
        for word in self.words:
            if word['german'].lower() == german.lower():
                return False, "Word already exists!"
        self.words.append({
            "id": len(self.words) + 1,
            "german": german.strip(),
            "english": english.strip(),
            "example": example.strip()
        })
        self.save_words()
        return True, f"Added: {german}"
    
    def delete_word(self, word_id):
        for i, word in enumerate(self.words):
            if word['id'] == word_id:
                self.words.pop(i)
                self.save_words()
                return True
        return False

# ---------- SESSION STATE ----------
if 'my_words_manager' not in st.session_state:
    st.session_state.my_words_manager = MyWordsManager()

manager = st.session_state.my_words_manager

# ---------- HEADER ----------
st.title("💾 My Words")
st.markdown("Your personal vocabulary collection")

# ---------- ADD WORD ----------
with st.expander("➕ Add New Word", expanded=False):
    with st.form("add_word_form"):
        col1, col2 = st.columns(2)
        with col1:
            german = st.text_input("🇩🇪 German Word:", placeholder="e.g., Haus")
        with col2:
            english = st.text_input("🇬🇧 English Translation:", placeholder="e.g., house")
        example = st.text_input("💬 Example Sentence (optional):", placeholder="Das Haus ist groß.")
        
        if st.form_submit_button("💾 Save Word", use_container_width=True):
            if german and english:
                success, message = manager.add_word(german, english, example)
                if success:
                    st.success(f"✅ {message}")
                    st.rerun()
                else:
                    st.error(f"❌ {message}")
            else:
                st.error("Please fill in both fields!")

st.divider()

# ---------- DISPLAY WORDS ----------
if manager.words:
    st.success(f"📚 {len(manager.words)} words saved")
    
    # Search filter
    search = st.text_input("🔍 Filter:", placeholder="Search in your words...")
    
    for word in manager.words:
        german = word.get('german', '').strip()
        english = word.get('english', '').strip()
        example = word.get('example', '').strip()
        
        if search and search.lower() not in german.lower() and search.lower() not in english.lower():
            continue
        
        with st.container(border=True):
            col1, col2 = st.columns([5, 1])
            with col1:
                st.markdown(f"**{german}**")
                st.caption(f"🇬🇧 {english}")
                if example:
                    st.caption(f"💬 {example}")
            with col2:
                if st.button(f"🗑️", key=f"remove_{word['id']}"):
                    if manager.delete_word(word['id']):
                        st.rerun()
    
    # Clear all
    if st.button("🗑️ Clear All Words", use_container_width=True):
        manager.words = []
        manager.save_words()
        st.rerun()
    
    # Export
    with st.expander("📤 Export"):
        json_str = json.dumps(manager.words, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Download as JSON",
            data=json_str,
            file_name="my_words.json",
            mime="application/json",
            use_container_width=True
        )
else:
    st.info("📭 No words saved yet. Search and save words from Vocabulary or Random Word!")
