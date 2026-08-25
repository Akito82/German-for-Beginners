# slang.py - German Slang Manager for Streamlit
"""Converted for Streamlit - Web-based slang display with search"""

import streamlit as st
import json
import os
import random
from gamification import gamification

class FastSlangManager:
    """Fast slang manager using JSON instead of Excel."""
    
    def __init__(self, json_path="data/slang.json"):
        """Initialize with path to JSON file."""
        self.json_path = json_path
        self.slang_data = []
        self.load_data()
    
    def load_data(self):
        """Load slang data from JSON file - much faster than Excel!"""
        print(f"\n📂 Loading slang data from: {self.json_path}")
        
        if not os.path.exists(self.json_path):
            error_msg = f"❌ File not found: {self.json_path}"
            print(error_msg)
            return False
        
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Extract slang words from the structure
            if 'slang_words' in data:
                self.slang_data = data['slang_words']
            else:
                self.slang_data = data
            
            print(f"✅ Successfully loaded {len(self.slang_data)} slang entries")
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Error reading JSON file: {e}")
            return False
        except Exception as e:
            print(f"❌ Error loading slang data: {e}")
            return False
    
    def get_random_slang(self):
        """Get a random slang entry - very fast!"""
        if not self.slang_data:
            return None
        
        try:
            return random.choice(self.slang_data)
        except Exception as e:
            print(f"❌ Error getting random slang: {e}")
            return None
    
    def get_total_count(self):
        """Get total number of slang entries."""
        return len(self.slang_data)
    
    def search_slang(self, search_term):
        """Search for slang containing the search term."""
        if not self.slang_data:
            return []
        
        search_term = search_term.lower()
        results = []
        
        for entry in self.slang_data:
            german = entry.get('german', '').lower()
            english = entry.get('english', '').lower()
            
            if search_term in german or search_term in english:
                results.append(entry)
        
        return results


# ---------- STREAMLIT UI ----------
def render_slang():
    """Render the Slang page in Streamlit."""
    
    # Initialize slang manager in session state
    if 'slang_manager' not in st.session_state:
        st.session_state.slang_manager = FastSlangManager("data/slang.json")
    
    if 'current_slang' not in st.session_state:
        st.session_state.current_slang = None
    
    if 'slang_search_results' not in st.session_state:
        st.session_state.slang_search_results = []
    
    manager = st.session_state.slang_manager
    
    # ---------- HEADER ----------
    st.title("🎭 Deutscher Slang & Umgangssprache")
    st.markdown("Learn everyday German slang and informal expressions!")
    
    # ---------- GAMIFICATION STATS ----------
    global_stats = gamification.get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("🏆 Global Level", global_stats.get('total_level', 1))
    with col2:
        st.metric("⭐ XP", global_stats.get('total_xp', 0))
    with col3:
        st.metric("📚 Slang Terms", manager.get_total_count())
    
    st.divider()
    
    # ---------- SIDEBAR - SEARCH ----------
    with st.sidebar:
        st.subheader("🔍 Search Slang")
        
        search_term = st.text_input(
            "Search for a slang term:",
            placeholder="e.g., geil, krass, etc.",
            key="slang_search_input"
        )
        
        if st.button("🔍 Search", use_container_width=True):
            if search_term:
                st.session_state.slang_search_results = manager.search_slang(search_term)
                if not st.session_state.slang_search_results:
                    st.info("No slang terms found matching your search.")
                st.rerun()
        
        if st.button("🔄 Show Random Slang", use_container_width=True):
            slang = manager.get_random_slang()
            if slang:
                st.session_state.current_slang = slang
                st.session_state.slang_search_results = []
                # Add XP for exploring slang
                gamification.add_xp("slang", 1, "Explored slang")
                st.rerun()
            else:
                st.error("No slang data loaded!")
        
        st.divider()
        
        # Stats
        st.caption(f"📊 Total slang entries: {manager.get_total_count()}")
    
    # ---------- MAIN CONTENT ----------
    
    # If there are search results, display them
    if st.session_state.slang_search_results:
        st.subheader(f"🔍 Search Results ({len(st.session_state.slang_search_results)})")
        
        for i, entry in enumerate(st.session_state.slang_search_results):
            with st.container(border=True):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"### 🇩🇪 {entry.get('german', '')}")
                    st.markdown(f"**🇬🇧 Meaning:** {entry.get('english', '')}")
                    if entry.get('example', ''):
                        st.caption(f"💬 *{entry.get('example', '')}*")
                    if entry.get('context', ''):
                        st.caption(f"📝 Context: {entry.get('context', '')}")
                with col2:
                    if st.button("🔊", key=f"slang_speak_search_{i}"):
                        # Try to speak the slang
                        try:
                            from gtts import gTTS
                            import tempfile
                            text = entry.get('german', '')
                            if text:
                                tts = gTTS(text=text, lang='de', slow=False)
                                with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                    tts.save(fp.name)
                                    audio_file = open(fp.name, 'rb')
                                    audio_bytes = audio_file.read()
                                    st.audio(audio_bytes, format='audio/mpeg')
                                    audio_file.close()
                        except:
                            st.info("🔊 Audio not available")
        
        # Clear results button
        if st.button("Clear Search Results", use_container_width=True):
            st.session_state.slang_search_results = []
            st.rerun()
    
    # Display current slang
    elif st.session_state.current_slang:
        display_slang_entry(st.session_state.current_slang)
    
    # Default: show random slang or welcome message
    else:
        # Auto-show a random slang on first visit
        if not st.session_state.current_slang:
            slang = manager.get_random_slang()
            if slang:
                st.session_state.current_slang = slang
                st.rerun()
            else:
                st.warning("No slang data loaded. Please check data/slang.json")
        
        # Display info if still no slang
        if not st.session_state.current_slang:
            with st.container(border=True):
                st.info("👈 Click 'Show Random Slang' in the sidebar to see a slang term!")
                st.markdown("""
                ### 💡 Tips:
                - Click the sidebar button to discover random German slang
                - Use the search bar to find specific slang terms
                - Listen to pronunciation with the 🔊 button
                - Learn informal German expressions used daily!
                """)


def display_slang_entry(slang):
    """Display a single slang entry with all details."""
    
    # Extract data
    german = slang.get('german', '')
    english = slang.get('english', '')
    example = slang.get('example', '')
    context = slang.get('context', '')
    source = slang.get('source', 'Unknown')
    
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])
        
        with col1:
            # Slang term
            st.markdown(f"## 🇩🇪 {german}")
            
            # English meaning
            st.markdown(f"**🇬🇧 Meaning:** {english}")
            
            # Example sentence
            if example:
                st.markdown(f"**💬 Example:** *{example}*")
            
            # Context
            if context:
                st.markdown(f"**📝 Context:** {context}")
            
            # Source
            st.caption(f"📦 Source: {source}")
        
        with col2:
            # Speaker button
            if st.button("🔊", key="slang_speak_current"):
                try:
                    from gtts import gTTS
                    import tempfile
                    if german:
                        tts = gTTS(text=german, lang='de', slow=False)
                        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                            tts.save(fp.name)
                            audio_file = open(fp.name, 'rb')
                            audio_bytes = audio_file.read()
                            st.audio(audio_bytes, format='audio/mpeg')
                            audio_file.close()
                except:
                    st.info("🔊 Audio not available")
    
    # Buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🎲 Another Slang", use_container_width=True):
            manager = st.session_state.slang_manager
            slang = manager.get_random_slang()
            if slang:
                st.session_state.current_slang = slang
                # Add XP for exploring
                gamification.add_xp("slang", 1, "Explored slang")
                st.rerun()
    
    with col2:
        if st.button("💾 Save to My Words", use_container_width=True):
            # Save slang to my_words
            if 'my_words_manager' in st.session_state:
                manager = st.session_state.my_words_manager
                success, message = manager.add_word(
                    german=german,
                    english=english,
                    example=example
                )
                if success:
                    st.success(f"✅ '{german}' added to My Words! (+5 XP)")
                    gamification.add_xp("my_words", 5, "Added slang to My Words")
                else:
                    st.warning(message)
            else:
                st.info("Go to My Words first to initialize your collection!")
    
    with col3:
        if st.button("📋 Copy", use_container_width=True):
            st.code(f"{german} = {english}", language="text")
            st.caption("Copied to clipboard!")


# ---------- PAGE FUNCTION ----------
def show_slang_page():
    """Page function for Streamlit navigation."""
    st.set_page_config(
        page_title="💬 Slang - German Learning",
        page_icon="💬",
        layout="wide"
    )
    
    render_slang()


# ---------- BACKWARD COMPATIBILITY ----------
def show_random_slang_window(parent_window, json_path="data/slang.json"):
    """
    Backward compatibility function.
    In Streamlit, we use render_slang() directly.
    """
    render_slang()


# ---------- TEST FUNCTION ----------
if __name__ == "__main__":
    print("🧪 Testing FastSlangManager...")
    
    # Test with default path
    manager = FastSlangManager("data/slang.json")
    
    if manager.slang_data:
        print(f"\n🎉 FastSlangManager test PASSED!")
        print(f"Loaded {len(manager.slang_data)} entries")
        print(f"First entry: {manager.slang_data[0].get('german', 'N/A')}")
        
        # Test random
        random_slang = manager.get_random_slang()
        print(f"Random slang: {random_slang.get('german', 'N/A')} = {random_slang.get('english', 'N/A')}")
    else:
        print("\n❌ FastSlangManager test FAILED")
