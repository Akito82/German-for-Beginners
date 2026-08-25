# my_words.py - Personal Vocabulary Manager for Streamlit
"""Converted for Streamlit - Web-based vocabulary management with learning sessions"""

import streamlit as st
import json
import os
import random
from datetime import datetime
from gamification import gamification

class MyWordsManager:
    """Manages the user's personal vocabulary with learning progress."""
    
    def __init__(self, data_file="data/my_words.json"):
        self.data_file = data_file
        self.words = []
        self.load_words()
    
    def load_words(self):
        """Load user's words from JSON file."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.words = json.load(f)
                print(f"✅ Loaded {len(self.words)} personal words")
            else:
                self.words = []
                print("ℹ️  No personal words file found, starting fresh")
        except Exception as e:
            print(f"❌ Error loading personal words: {e}")
            self.words = []
    
    def save_words(self):
        """Save user's words to JSON file."""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.words, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"❌ Error saving personal words: {e}")
            return False
    
    def add_word(self, german, english, example=""):
        """Add a new word to personal collection."""
        # Check for duplicates
        for word in self.words:
            if word['german'].lower() == german.lower():
                return False, "German word already exists!"
        
        new_word = {
            "id": len(self.words) + 1,
            "german": german.strip(),
            "english": english.strip(),
            "example": example.strip(),
            "added_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "learning_level": 0,  # 0 = new, 5 = mastered
            "correct_count": 0,
            "wrong_count": 0
        }
        
        self.words.append(new_word)
        self.save_words()
        
        # Add XP for adding a new word
        gamification.add_xp("my_words", 5, "Added new word")
        
        return True, f"Added: {german} = {english}"
    
    def get_random_word(self):
        """Get a completely random word from collection."""
        if not self.words:
            return None
        return random.choice(self.words)
    
    def get_words_by_level(self, level):
        """Get words with a specific learning level."""
        return [w for w in self.words if w.get('learning_level', 0) == level]
    
    def update_word_score(self, word_id, correct):
        """Update word's learning score."""
        for word in self.words:
            if word['id'] == word_id:
                if correct:
                    word['correct_count'] = word.get('correct_count', 0) + 1
                    # Increase learning level (max 5)
                    word['learning_level'] = min(5, word.get('learning_level', 0) + 1)
                else:
                    word['wrong_count'] = word.get('wrong_count', 0) + 1
                    # Decrease learning level (min 0)
                    word['learning_level'] = max(0, word.get('learning_level', 0) - 1)
                
                self.save_words()
                return True
        return False
    
    def get_stats(self):
        """Get simple statistics."""
        if not self.words:
            return {"total": 0, "levels": [0]*6}
        
        levels = [0]*6
        for word in self.words:
            level = word.get('learning_level', 0)
            levels[min(level, 5)] += 1
        
        return {
            "total": len(self.words),
            "levels": levels
        }
    
    def get_level_color(self, level):
        """Get color for learning level."""
        colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60', '#16a085']
        return colors[min(level, 5)]
    
    def get_level_name(self, level):
        """Get name for learning level."""
        names = ['New', 'Beginner', 'Learning', 'Familiar', 'Proficient', 'Mastered']
        return names[min(level, 5)]
    
    def delete_word(self, word_id):
        """Delete a word from the collection."""
        for i, word in enumerate(self.words):
            if word['id'] == word_id:
                self.words.pop(i)
                self.save_words()
                return True
        return False


# ---------- STREAMLIT UI ----------
def render_my_words():
    """Render the My Words page in Streamlit."""
    
    # Initialize manager in session state
    if 'my_words_manager' not in st.session_state:
        st.session_state.my_words_manager = MyWordsManager()
    
    if 'my_words_view' not in st.session_state:
        st.session_state.my_words_view = "main"  # main, add, learn
    
    if 'learn_session_active' not in st.session_state:
        st.session_state.learn_session_active = False
    
    manager = st.session_state.my_words_manager
    
    # ---------- HEADER ----------
    st.title("📖 Meine Wörter")
    st.markdown("Your personal German vocabulary collection")
    
    # ---------- GAMIFICATION STATS ----------
    global_stats = gamification.get_stats()
    my_words_stats = gamification.get_stats("my_words")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Global Level", global_stats.get('total_level', 1))
    with col2:
        st.metric("⭐ XP", global_stats.get('total_xp', 0))
    with col3:
        st.metric("📚 My Words", len(manager.words))
    with col4:
        st.metric("🎯 Words Level", my_words_stats.get('level', 1))
    
    st.divider()
    
    # ---------- NAVIGATION ----------
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📋 Overview", use_container_width=True):
            st.session_state.my_words_view = "main"
            st.rerun()
    with col2:
        if st.button("➕ Add Word", use_container_width=True):
            st.session_state.my_words_view = "add"
            st.rerun()
    with col3:
        if st.button("🎓 Learn", use_container_width=True):
            if manager.words:
                st.session_state.my_words_view = "learn"
                st.session_state.learn_session_active = True
                st.rerun()
            else:
                st.warning("No words to learn! Add some words first.")
    
    st.divider()
    
    # ---------- VIEW: MAIN (Overview) ----------
    if st.session_state.my_words_view == "main":
        stats = manager.get_stats()
        
        # Show stats
        if stats["total"] == 0:
            st.info("📭 No words in your collection yet. Add your first word!")
        else:
            st.success(f"📚 You have {stats['total']} words in your collection")
            
            # Level distribution
            st.subheader("📊 Learning Progress")
            
            # Create progress bars for each level
            level_names = ['New', 'Beginner', 'Learning', 'Familiar', 'Proficient', 'Mastered']
            level_colors = ['#e74c3c', '#e67e22', '#f1c40f', '#2ecc71', '#27ae60', '#16a085']
            
            for level in range(6):
                count = stats['levels'][level]
                percentage = (count / stats['total'] * 100) if stats['total'] > 0 else 0
                
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    st.markdown(f"**{level_names[level]}**")
                with col2:
                    st.progress(percentage / 100)
                with col3:
                    st.caption(f"{count} words")
            
            # Word list
            with st.expander(f"📖 Show All {stats['total']} Words", expanded=False):
                for word in manager.words:
                    level = word.get('learning_level', 0)
                    color = manager.get_level_color(level)
                    level_name = manager.get_level_name(level)
                    
                    with st.container(border=True):
                        col1, col2, col3 = st.columns([4, 2, 1])
                        with col1:
                            st.markdown(f"**{word['german']}**")
                            st.caption(f"🇬🇧 {word['english']}")
                            if word.get('example'):
                                st.caption(f"💬 {word['example']}")
                        with col2:
                            st.markdown(f"<span style='color:{color};'>● {level_name}</span>", 
                                       unsafe_allow_html=True)
                            st.caption(f"✅ {word.get('correct_count', 0)} correct")
                            st.caption(f"❌ {word.get('wrong_count', 0)} wrong")
                        with col3:
                            if st.button(f"🗑️", key=f"delete_{word['id']}"):
                                if manager.delete_word(word['id']):
                                    st.success(f"Deleted '{word['german']}'")
                                    st.rerun()
    
    # ---------- VIEW: ADD WORD ----------
    elif st.session_state.my_words_view == "add":
        st.subheader("➕ Add New Word")
        
        with st.form("add_word_form"):
            german = st.text_input("🇩🇪 German Word:", placeholder="e.g., Haus")
            english = st.text_input("🇬🇧 English Translation:", placeholder="e.g., house")
            example = st.text_input("💬 Example Sentence (optional):", placeholder="Das Haus ist groß.")
            
            col1, col2 = st.columns(2)
            with col1:
                submitted = st.form_submit_button("💾 Save Word", use_container_width=True)
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    st.session_state.my_words_view = "main"
                    st.rerun()
            
            if submitted:
                if not german or not english:
                    st.error("❌ Please fill in both German and English fields!")
                else:
                    success, message = manager.add_word(german, english, example)
                    if success:
                        st.success(f"✅ {message} (+5 XP)")
                        st.balloons()
                        # Clear form fields by rerunning
                        st.session_state.my_words_view = "main"
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
        
        if st.button("← Back to Overview"):
            st.session_state.my_words_view = "main"
            st.rerun()
    
    # ---------- VIEW: LEARNING SESSION ----------
    elif st.session_state.my_words_view == "learn":
        st.subheader("✍️ Learning Session")
        
        # Initialize session state for learning
        if 'learn_session' not in st.session_state:
            st.session_state.learn_session = {
                "correct": 0,
                "total": 0,
                "streak": 0,
                "best_streak": 0,
                "session_xp": 0,
                "current_word": None,
                "direction": None,
                "expected_answer": "",
                "answered": False,
                "feedback": "",
                "feedback_color": "green"
            }
        
        session = st.session_state.learn_session
        
        # Show session stats
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            accuracy = (session["correct"] / session["total"] * 100) if session["total"] > 0 else 0
            st.metric("✅ Accuracy", f"{accuracy:.0f}%")
        with col2:
            st.metric("📝 Questions", session["total"])
        with col3:
            st.metric("🔥 Streak", session["streak"])
        with col4:
            st.metric("⭐ Session XP", f"+{session['session_xp']}")
        
        st.divider()
        
        # ---------- LEARNING SESSION LOGIC ----------
        
        # If no current word or answered, get a new one
        if session["current_word"] is None or session.get("answered", False):
            # Get a random word
            word = manager.get_random_word()
            if word:
                session["current_word"] = word
                session["answered"] = False
                session["feedback"] = ""
                
                # Random direction
                direction = random.choice(['de-en', 'en-de'])
                session["direction"] = direction
                
                if direction == 'de-en':
                    session["expected_answer"] = word['english'].lower().strip()
                else:
                    session["expected_answer"] = word['german'].lower().strip()
            else:
                st.warning("No words to learn! Add some words first.")
                if st.button("← Back"):
                    st.session_state.my_words_view = "main"
                    st.rerun()
                return
        
        # Display current word
        word = session["current_word"]
        direction = session["direction"]
        
        # Show question
        with st.container(border=True):
            if direction == 'de-en':
                st.markdown("#### Translate to English:")
                st.markdown(f"<h2 style='color:#e74c3c;'>🇩🇪 {word['german']}</h2>", unsafe_allow_html=True)
            else:
                st.markdown("#### Translate to German:")
                st.markdown(f"<h2 style='color:#3498db;'>🇬🇧 {word['english']}</h2>", unsafe_allow_html=True)
            
            # Show example if available
            if word.get('example'):
                st.caption(f"💬 Example: {word['example']}")
            
            # Learning level indicator
            level = word.get('learning_level', 0)
            color = manager.get_level_color(level)
            level_name = manager.get_level_name(level)
            st.markdown(f"<span style='color:{color};'>● Level: {level_name}</span>", unsafe_allow_html=True)
        
        # Show feedback
        if session.get("feedback"):
            if "✅" in session["feedback"]:
                st.success(session["feedback"])
            elif "❌" in session["feedback"]:
                st.error(session["feedback"])
            else:
                st.info(session["feedback"])
        
        # Answer input
        if not session.get("answered", False):
            col1, col2 = st.columns([3, 1])
            with col1:
                answer = st.text_input(
                    "Your answer:",
                    placeholder="Type your answer here...",
                    key="learn_answer",
                    autocomplete="off"
                )
            with col2:
                st.write("")
                st.write("")
                submit = st.button("📤 Check", use_container_width=True)
            
            if submit and answer:
                # Check answer
                user_answer = answer.lower().strip()
                expected = session["expected_answer"]
                
                # Allow multiple correct answers (if multiple translations)
                is_correct = user_answer == expected
                
                # Update session stats
                session["total"] += 1
                
                if is_correct:
                    # Correct!
                    session["correct"] += 1
                    session["streak"] += 1
                    
                    if session["streak"] > session["best_streak"]:
                        session["best_streak"] = session["streak"]
                    
                    # Calculate XP
                    base_xp = 1
                    streak_bonus = min(session["streak"] // 5, 3)
                    xp_earned = base_xp + streak_bonus
                    session["session_xp"] += xp_earned
                    
                    # Add to gamification
                    gamification.add_xp("my_words", xp_earned, "Correct answer in learning session")
                    gamification.add_correct_answer("my_words")
                    
                    # Update word score
                    manager.update_word_score(word['id'], True)
                    
                    # Build feedback
                    if streak_bonus > 0:
                        session["feedback"] = f"✅ Richtig! +{xp_earned} XP (Streak bonus: +{streak_bonus} XP)"
                    else:
                        session["feedback"] = f"✅ Richtig! +{xp_earned} XP"
                    
                else:
                    # Wrong
                    session["streak"] = 0
                    
                    # Update word score
                    manager.update_word_score(word['id'], False)
                    
                    session["feedback"] = f"❌ Wrong! The answer was: {expected.title()}"
                
                session["answered"] = True
                st.rerun()
        
        else:
            # Show next button after answering
            if st.button("➡️ Next Word", use_container_width=True):
                session["current_word"] = None
                session["answered"] = False
                session["feedback"] = ""
                st.rerun()
        
        # ---------- SESSION CONTROLS ----------
        st.divider()
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔄 Reset Session", use_container_width=True):
                st.session_state.learn_session = {
                    "correct": 0,
                    "total": 0,
                    "streak": 0,
                    "best_streak": 0,
                    "session_xp": 0,
                    "current_word": None,
                    "direction": None,
                    "expected_answer": "",
                    "answered": False,
                    "feedback": "",
                    "feedback_color": "green"
                }
                st.rerun()
        
        with col2:
            if st.button("← End Session", use_container_width=True):
                # Show summary
                accuracy = (session["correct"] / session["total"] * 100) if session["total"] > 0 else 0
                
                st.success(f"""
                📊 Session Summary
                
                - Questions: {session['total']}
                - Correct: {session['correct']}
                - Accuracy: {accuracy:.1f}%
                - Best Streak: {session['best_streak']}
                - Session XP: +{session['session_xp']}
                """)
                
                st.session_state.my_words_view = "main"
                st.session_state.learn_session_active = False
                st.rerun()

# ---------- PAGE FUNCTION ----------
def show_my_words_page():
    """Page function for Streamlit navigation."""
    st.set_page_config(
        page_title="💾 My Words - German Learning",
        page_icon="💾",
        layout="wide"
    )
    
    render_my_words()


# ---------- BACKWARD COMPATIBILITY ----------
def show_my_words_window(parent_window, main_vocabulary=None):
    """
    Backward compatibility function.
    In Streamlit, we use render_my_words() directly.
    """
    render_my_words()
