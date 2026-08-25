# hangman.py - Hangman Game for Streamlit
"""Converted for Streamlit - Web-based Hangman with gamification"""

import streamlit as st
import random
import json
import os
from gamification import gamification

class HangmanGame:
    """Hangman game logic - Streamlit version"""
    
    def __init__(self, vocabulary_list):
        self.vocabulary = vocabulary_list
        self.current_word = ""
        self.current_translation = ""
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.max_wrong = 8
        self.game_over = False
        self.game_won = False
        
        # Session stats
        self.session_stats = {
            "games_played": 0,
            "games_won": 0,
            "current_streak": 0,
            "best_streak": 0,
            "total_letters_guessed": 0,
            "session_xp": 0
        }
    
    def get_hangman_word(self):
        """Get a word suitable for hangman with translation."""
        suitable_words = []
        
        for word_entry in self.vocabulary:
            german_word = word_entry.get('german', '').strip().upper()
            english_translation = word_entry.get('english', '').strip()
            
            if (3 <= len(german_word) <= 12 and
                all(c.isalpha() or c in 'ÄÖÜ' for c in german_word) and
                ' ' not in german_word and
                english_translation):
                suitable_words.append(word_entry)
        
        if suitable_words:
            return random.choice(suitable_words)
        elif self.vocabulary:
            return random.choice(self.vocabulary)
        return None
    
    def new_game(self):
        """Start a new game with a random word."""
        word_entry = self.get_hangman_word()
        
        if not word_entry:
            return False
        
        self.current_word = word_entry.get('german', '').strip().upper()
        self.current_translation = word_entry.get('english', '').strip()
        self.guessed_letters = set()
        self.wrong_guesses = 0
        self.game_over = False
        self.game_won = False
        
        return True
    
    def guess_letter(self, letter):
        """Handle a letter guess."""
        if self.game_over:
            return False, "Game is already over!"
        
        if letter in self.guessed_letters:
            return False, "Letter already guessed!"
        
        self.guessed_letters.add(letter)
        
        if letter in self.current_word:
            self.session_stats["total_letters_guessed"] += 1
            return True, "Correct!"
        else:
            self.wrong_guesses += 1
            return False, "Wrong!"
    
    def check_game_over(self):
        """Check if the game is won or lost."""
        # Check win
        if all(c in self.guessed_letters or not c.isalpha() for c in self.current_word):
            self.game_over = True
            self.game_won = True
            return "win"
        
        # Check loss
        if self.wrong_guesses >= self.max_wrong:
            self.game_over = True
            self.game_won = False
            return "loss"
        
        return "continue"
    
    def get_display_word(self):
        """Get the word with guessed letters revealed."""
        display = ""
        for char in self.current_word:
            if char in self.guessed_letters or not char.isalpha():
                display += char + " "
            else:
                display += "_ "
        return display.strip()
    
    def get_remaining_letters(self):
        """Get count of remaining letters to guess."""
        return len([c for c in self.current_word if c.isalpha() and c not in self.guessed_letters])
    
    def calculate_xp_for_win(self):
        """Calculate XP for winning a hangman game."""
        base_xp = 5
        perfect_bonus = 3 if self.wrong_guesses == 0 else 0
        length_bonus = min(len(self.current_word) // 3, 4)
        streak_bonus = min(self.session_stats["current_streak"] // 3, 5)
        
        total_xp = base_xp + perfect_bonus + length_bonus + streak_bonus
        
        return total_xp, {
            "base": base_xp,
            "perfect_bonus": perfect_bonus,
            "length_bonus": length_bonus,
            "streak_bonus": streak_bonus
        }


# ---------- HANGMAN UI ----------
def render_hangman():
    """Render the Hangman game in Streamlit."""
    
    # Initialize game in session state
    if 'hangman_game' not in st.session_state:
        # Load vocabulary from session state
        vocab = st.session_state.get('vocabulary', [])
        st.session_state.hangman_game = HangmanGame(vocab)
        st.session_state.hangman_started = False
    
    if 'hangman_letter_buttons' not in st.session_state:
        st.session_state.hangman_letter_buttons = {}
    
    if 'hangman_feedback' not in st.session_state:
        st.session_state.hangman_feedback = ""
    
    game = st.session_state.hangman_game
    
    # ---------- HEADER ----------
    st.title("🎯 Galgenmännchen (Hangman)")
    st.markdown("Guess the German word letter by letter!")
    
    # ---------- GAMIFICATION STATS ----------
    col1, col2, col3, col4 = st.columns(4)
    
    global_stats = gamification.get_stats()
    global_level = global_stats.get('total_level', 1)
    global_xp = global_stats.get('total_xp', 0)
    
    with col1:
        st.metric("🏆 Level", f"{global_level}")
    with col2:
        st.metric("⭐ XP", f"{global_xp}")
    with col3:
        won = game.session_stats["games_won"]
        played = game.session_stats["games_played"]
        win_rate = (won / played * 100) if played > 0 else 0
        st.metric("🎯 Win Rate", f"{win_rate:.0f}%")
    with col4:
        st.metric("🔥 Streak", f"{game.session_stats['current_streak']}")
    
    # ---------- SESSION STATS ----------
    with st.expander("📊 Session Stats"):
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Games Played", game.session_stats["games_played"])
            st.metric("Games Won", game.session_stats["games_won"])
        with col2:
            st.metric("Best Streak", game.session_stats["best_streak"])
            st.metric("Session XP", f"+{game.session_stats['session_xp']}")
        with col3:
            st.metric("Letters Guessed", game.session_stats["total_letters_guessed"])
            st.metric("Wrong Guesses", f"{game.wrong_guesses}/{game.max_wrong}")
    
    st.divider()
    
    # ---------- START / NEW GAME ----------
    if not st.session_state.hangman_started or game.game_over:
        if st.button("🔄 New Word", use_container_width=True):
            if game.new_game():
                st.session_state.hangman_started = True
                st.session_state.hangman_feedback = ""
                st.rerun()
            else:
                st.error("No suitable words found in vocabulary!")
        st.info("Click 'New Word' to start a new game!")
        return
    
    # ---------- ENGLISH HINT ----------
    st.markdown(f"**💡 English Translation:** _{game.current_translation}_")
    
    # ---------- WORD DISPLAY ----------
    st.markdown("### Guess the German word:")
    display_word = game.get_display_word()
    st.markdown(f"<h1 style='text-align: center; color: #e74c3c; font-family: monospace;'>{display_word}</h1>", 
                unsafe_allow_html=True)
    
    # ---------- HANGMAN DRAWING ----------
    st.markdown("### Hangman Status")
    
    # Draw hangman using ASCII art
    hangman_stages = [
        """
           -----
           |   |
               |
               |
               |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
               |
               |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
           |   |
               |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
          /|   |
               |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
               |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
          /    |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
          / \\  |
               |
        =========
        """,
        """
           -----
           |   |
           O   |
          /|\\  |
          / \\  |
          ✗    |
        =========
        """,
        """
           -----
           |   |
           💀   |
          /|\\  |
          / \\  |
               |
        =========
        """
    ]
    
    # Show the appropriate hangman stage
    stage_index = min(game.wrong_guesses, len(hangman_stages) - 1)
    st.code(hangman_stages[stage_index], language="text")
    
    # ---------- STATUS ----------
    remaining = game.get_remaining_letters()
    st.caption(f"Wrong guesses: {game.wrong_guesses}/{game.max_wrong} | Letters remaining: {remaining}")
    
    # ---------- FEEDBACK ----------
    if st.session_state.hangman_feedback:
        if "Correct" in st.session_state.hangman_feedback:
            st.success(st.session_state.hangman_feedback)
        elif "Wrong" in st.session_state.hangman_feedback:
            st.warning(st.session_state.hangman_feedback)
        elif "Already" in st.session_state.hangman_feedback:
            st.info(st.session_state.hangman_feedback)
    
    # ---------- KEYBOARD ----------
    st.markdown("### Choose a letter:")
    
    # German alphabet
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÜ"
    
    # Create rows of buttons
    cols = st.columns(9)
    for i, letter in enumerate(alphabet):
        with cols[i % 9]:
            # Check if letter already guessed
            if letter in game.guessed_letters:
                # Show guessed letter with color feedback
                if letter in game.current_word:
                    st.button(
                        letter, 
                        key=f"hangman_{letter}",
                        disabled=True,
                        use_container_width=True,
                        type="primary" if letter in game.current_word else "secondary"
                    )
                else:
                    st.button(
                        letter, 
                        key=f"hangman_{letter}",
                        disabled=True,
                        use_container_width=True,
                        type="secondary"
                    )
            else:
                # Available letter
                if st.button(
                    letter,
                    key=f"hangman_{letter}",
                    use_container_width=True,
                    type="primary"
                ):
                    # Handle guess
                    is_correct, feedback = game.guess_letter(letter)
                    st.session_state.hangman_feedback = feedback
                    
                    # Check game over
                    result = game.check_game_over()
                    
                    if result == "win":
                        # Handle win
                        game.session_stats["games_played"] += 1
                        game.session_stats["games_won"] += 1
                        game.session_stats["current_streak"] += 1
                        
                        if game.session_stats["current_streak"] > game.session_stats["best_streak"]:
                            game.session_stats["best_streak"] = game.session_stats["current_streak"]
                        
                        # Calculate XP
                        total_xp, xp_breakdown = game.calculate_xp_for_win()
                        game.session_stats["session_xp"] += total_xp
                        
                        # Add to gamification
                        gamification.add_xp("hangman", total_xp, "Won hangman game")
                        gamification.add_correct_answer("hangman")
                        gamification.update_best_score("hangman", game.session_stats["current_streak"])
                        
                        # Store for display
                        st.session_state.hangman_xp_breakdown = xp_breakdown
                        st.session_state.hangman_total_xp = total_xp
                        st.rerun()
                    
                    elif result == "loss":
                        # Handle loss
                        game.session_stats["games_played"] += 1
                        game.session_stats["current_streak"] = 0
                        
                        # Consolation XP
                        consolation_xp = 1
                        game.session_stats["session_xp"] += consolation_xp
                        gamification.add_xp("hangman", consolation_xp, "Lost hangman game")
                        
                        st.rerun()
                    else:
                        st.rerun()
    
    # ---------- GAME OVER DISPLAY ----------
    if game.game_over:
        st.divider()
        
        if game.game_won:
            st.balloons()
            st.success(f"🎉 You won! The word was: **{game.current_word}**")
            st.markdown(f"🇬🇧 {game.current_translation}")
            
            # Show XP breakdown
            if hasattr(st.session_state, 'hangman_xp_breakdown'):
                with st.expander("🏆 XP Details"):
                    breakdown = st.session_state.hangman_xp_breakdown
                    st.write(f"• Base: +{breakdown['base']} XP")
                    if breakdown.get('perfect_bonus', 0) > 0:
                        st.write(f"• Perfect game: +{breakdown['perfect_bonus']} XP")
                    if breakdown.get('length_bonus', 0) > 0:
                        st.write(f"• Word length: +{breakdown['length_bonus']} XP")
                    if breakdown.get('streak_bonus', 0) > 0:
                        st.write(f"• Win streak: +{breakdown['streak_bonus']} XP")
                    st.write(f"**Total: +{st.session_state.hangman_total_xp} XP**")
        else:
            st.error(f"💀 Game Over! The word was: **{game.current_word}**")
            st.markdown(f"🇬🇧 {game.current_translation}")
            st.info(f"💡 Consolation XP: +1")
        
        # New game button
        if st.button("🔄 Play Again", use_container_width=True):
            game.new_game()
            st.session_state.hangman_feedback = ""
            st.session_state.hangman_started = True
            if hasattr(st.session_state, 'hangman_xp_breakdown'):
                del st.session_state.hangman_xp_breakdown
            if hasattr(st.session_state, 'hangman_total_xp'):
                del st.session_state.hangman_total_xp
            st.rerun()
    
    # ---------- HINT BUTTON ----------
    if not game.game_over:
        if st.button("💡 Show Hint (reveal a letter)", use_container_width=True):
            # Find unguessed letters
            unguessed = [c for c in game.current_word 
                        if c.isalpha() and c not in game.guessed_letters]
            
            if unguessed:
                hint_letter = random.choice(unguessed)
                # Auto-guess the letter
                is_correct, feedback = game.guess_letter(hint_letter)
                st.session_state.hangman_feedback = f"Hint: '{hint_letter}' revealed!"
                
                # Check game over
                result = game.check_game_over()
                if result == "win" or result == "loss":
                    st.rerun()
                st.rerun()
            else:
                st.info("No letters left to reveal!")


# ---------- PAGE FUNCTION ----------
def show_hangman_page():
    """Page function for Streamlit navigation."""
    st.set_page_config(
        page_title="🪢 Hangman - German Learning",
        page_icon="🪢",
        layout="wide"
    )
    
    render_hangman()


# ---------- START FUNCTION (Backward Compatibility) ----------
def start_hangman(parent_window, vocabulary):
    """
    Backward compatibility function.
    In Streamlit, we use render_hangman() directly.
    """
    # Store vocabulary in session state for the game to use
    st.session_state.hangman_vocab = vocabulary
    render_hangman()
