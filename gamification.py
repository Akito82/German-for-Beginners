# gamification.py - Centralized gamification system for Streamlit
"""Converted for Streamlit - uses session state instead of file-based storage"""

import json
import os
from datetime import datetime
import streamlit as st

class GamificationManager:
    """Manages user progress, levels, and XP across all games."""
    
    def __init__(self, data_file="data/gamification.json"):
        self.data_file = data_file
        # For Streamlit, we store progress in session state
        self._ensure_session_state()
    
    def _ensure_session_state(self):
        """Initialize gamification data in session state if not exists."""
        if 'gamification_data' not in st.session_state:
            st.session_state.gamification_data = self._load_default_progress()
        if 'gamification_loaded' not in st.session_state:
            st.session_state.gamification_loaded = False
    
    def _load_default_progress(self):
        """Create default progress structure."""
        return {
            "global": {
                "total_xp": 0,
                "total_level": 1,
                "total_games_played": 0,
                "total_correct_answers": 0,
                "first_login": datetime.now().isoformat(),
                "last_login": datetime.now().isoformat()
            },
            "games": {
                "word_builder": {
                    "xp": 0,
                    "level": 1,
                    "games_played": 0,
                    "best_score": 0,
                    "correct_answers": 0
                },
                "word_order": {
                    "xp": 0,
                    "level": 1,
                    "games_played": 0,
                    "best_score": 0,
                    "correct_answers": 0
                },
                "hangman": {
                    "xp": 0,
                    "level": 1,
                    "games_played": 0,
                    "best_score": 0,
                    "correct_answers": 0
                },
                "german_quiz": {
                    "xp": 0,
                    "level": 1,
                    "games_played": 0,
                    "best_score": 0,
                    "correct_answers": 0
                },
                "my_words": {
                    "xp": 0,
                    "level": 1,
                    "games_played": 0,
                    "best_score": 0,
                    "correct_answers": 0
                }
            },
            "achievements": {
                "first_game": False,
                "level_5": False,
                "level_10": False,
                "perfect_game": False,
                "streak_5": False,
                "streak_10": False
            }
        }
    
    def _load_from_file(self):
        """Load gamification progress from JSON file (optional persistence)."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Ensure all games have required fields
                    for game_name, game_data in data.get("games", {}).items():
                        if "games_played" not in game_data:
                            game_data["games_played"] = 0
                        if "best_score" not in game_data:
                            game_data["best_score"] = 0
                        if "correct_answers" not in game_data:
                            game_data["correct_answers"] = 0
                    
                    return data
        except Exception as e:
            print(f"⚠️ Could not load gamification file: {e}")
        
        return None
    
    def _save_to_file(self, data):
        """Save gamification progress to JSON file (optional persistence)."""
        try:
            os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
            
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"⚠️ Could not save gamification file: {e}")
            return False
    
    def load_progress(self):
        """Load progress from session state or file."""
        # First try to load from file (if user wants persistence)
        file_data = self._load_from_file()
        if file_data:
            st.session_state.gamification_data = file_data
        
        if 'gamification_data' not in st.session_state:
            st.session_state.gamification_data = self._load_default_progress()
        
        st.session_state.gamification_loaded = True
        return st.session_state.gamification_data
    
    def save_progress(self, data=None):
        """Save gamification progress."""
        if data is None:
            data = st.session_state.gamification_data
        
        # Update last login
        data["global"]["last_login"] = datetime.now().isoformat()
        
        # Update session state
        st.session_state.gamification_data = data
        
        # Optionally save to file for persistence across sessions
        self._save_to_file(data)
        
        return True
    
    @property
    def progress(self):
        """Get current progress data."""
        if 'gamification_data' not in st.session_state:
            self.load_progress()
        return st.session_state.gamification_data
    
    def calculate_level_from_xp(self, xp):
        """Calculate level based on XP using a progressive formula."""
        level = 1
        xp_needed = 0
        
        while True:
            next_level_needed = xp_needed + (level + 1) * 100
            if xp < next_level_needed:
                break
            level += 1
            xp_needed = next_level_needed
        
        # XP needed for next level
        next_level_xp = xp_needed + (level + 1) * 100
        xp_to_next = next_level_xp - xp
        
        return level, xp_to_next
    
    def add_xp(self, game_name, xp_amount, reason=""):
        """Add XP to a specific game and update global totals."""
        data = self.progress
        
        if game_name not in data["games"]:
            data["games"][game_name] = {
                "xp": 0,
                "level": 1,
                "games_played": 0,
                "best_score": 0,
                "correct_answers": 0
            }
        
        # Ensure required fields exist
        if "games_played" not in data["games"][game_name]:
            data["games"][game_name]["games_played"] = 0
        if "correct_answers" not in data["games"][game_name]:
            data["games"][game_name]["correct_answers"] = 0
        
        # Add XP to game
        data["games"][game_name]["xp"] += xp_amount
        
        # Update game level
        current_xp = data["games"][game_name]["xp"]
        game_level, _ = self.calculate_level_from_xp(current_xp)
        data["games"][game_name]["level"] = game_level
        
        # Add to global XP
        data["global"]["total_xp"] += xp_amount
        
        # Update global level
        total_xp = data["global"]["total_xp"]
        global_level, _ = self.calculate_level_from_xp(total_xp)
        data["global"]["total_level"] = global_level
        
        # Update game played counter
        data["games"][game_name]["games_played"] += 1
        data["global"]["total_games_played"] += 1
        
        # Check for achievements
        unlocked = self.check_achievements()
        
        # Save changes
        self.save_progress(data)
        
        return {
            "game_xp": data["games"][game_name]["xp"],
            "game_level": game_level,
            "total_xp": data["global"]["total_xp"],
            "total_level": global_level,
            "achievements_unlocked": unlocked,
            "xp_to_next_level": self.calculate_level_from_xp(game_level * 100)[1]  # Approximate
        }
    
    def add_correct_answer(self, game_name):
        """Record a correct answer."""
        data = self.progress
        
        data["global"]["total_correct_answers"] += 1
        
        if game_name in data["games"]:
            if "correct_answers" not in data["games"][game_name]:
                data["games"][game_name]["correct_answers"] = 0
            data["games"][game_name]["correct_answers"] += 1
        
        self.save_progress(data)
    
    def update_best_score(self, game_name, score):
        """Update the best score for a game."""
        data = self.progress
        
        if game_name in data["games"]:
            current_best = data["games"][game_name].get("best_score", 0)
            if score > current_best:
                data["games"][game_name]["best_score"] = score
                self.save_progress(data)
                return True
        return False
    
    def check_achievements(self):
        """Check and unlock achievements."""
        data = self.progress
        achievements_unlocked = []
        
        # Level achievements
        if data["global"]["total_level"] >= 5 and not data["achievements"]["level_5"]:
            data["achievements"]["level_5"] = True
            achievements_unlocked.append("Level 5 erreicht! 🎉")
        
        if data["global"]["total_level"] >= 10 and not data["achievements"]["level_10"]:
            data["achievements"]["level_10"] = True
            achievements_unlocked.append("Level 10 erreicht! 🚀")
        
        # First game achievement
        if data["global"]["total_games_played"] >= 1 and not data["achievements"]["first_game"]:
            data["achievements"]["first_game"] = True
            achievements_unlocked.append("Erstes Spiel gespielt! 🎮")
        
        # Perfect game achievement (if implemented)
        if data["global"]["total_correct_answers"] >= 10 and not data["achievements"]["perfect_game"]:
            data["achievements"]["perfect_game"] = True
            achievements_unlocked.append("10 richtige Antworten! ⭐")
        
        # Save if any achievements were unlocked
        if achievements_unlocked:
            self.save_progress(data)
        
        return achievements_unlocked
    
    def get_stats(self, game_name=None):
        """Get statistics for a specific game or global stats."""
        data = self.progress
        
        if game_name and game_name in data["games"]:
            stats = data["games"][game_name].copy()
            # Add XP to next level
            _, xp_to_next = self.calculate_level_from_xp(stats.get("xp", 0))
            stats["xp_to_next_level"] = xp_to_next
            return stats
        else:
            stats = data["global"].copy()
            # Add XP to next level
            _, xp_to_next = self.calculate_level_from_xp(stats.get("total_xp", 0))
            stats["xp_to_next_level"] = xp_to_next
            return stats
    
    def get_achievements(self):
        """Get all achievements and their status."""
        data = self.progress
        achievements = data.get("achievements", {})
        
        # Format for display
        achievement_info = {
            "first_game": {
                "name": "Erstes Spiel",
                "description": "Spiele dein erstes Spiel",
                "unlocked": achievements.get("first_game", False),
                "icon": "🎮"
            },
            "level_5": {
                "name": "Level 5",
                "description": "Erreiche Level 5",
                "unlocked": achievements.get("level_5", False),
                "icon": "⭐"
            },
            "level_10": {
                "name": "Level 10",
                "description": "Erreiche Level 10",
                "unlocked": achievements.get("level_10", False),
                "icon": "🚀"
            },
            "perfect_game": {
                "name": "Perfektes Spiel",
                "description": "10 richtige Antworten",
                "unlocked": achievements.get("perfect_game", False),
                "icon": "🏆"
            },
            "streak_5": {
                "name": "5er Serie",
                "description": "5 Spiele in Folge gewinnen",
                "unlocked": achievements.get("streak_5", False),
                "icon": "🔥"
            },
            "streak_10": {
                "name": "10er Serie",
                "description": "10 Spiele in Folge gewinnen",
                "unlocked": achievements.get("streak_10", False),
                "icon": "💎"
            }
        }
        
        return achievement_info
    
    def get_all_stats(self):
        """Get all gamification data."""
        return self.progress
    
    def reset_progress(self):
        """Reset all progress."""
        st.session_state.gamification_data = self._load_default_progress()
        self.save_progress(st.session_state.gamification_data)
        return True
    
    def get_level_progress(self, game_name=None):
        """Get progress bar data for level advancement."""
        if game_name and game_name in self.progress["games"]:
            xp = self.progress["games"][game_name]["xp"]
            level = self.progress["games"][game_name]["level"]
        else:
            xp = self.progress["global"]["total_xp"]
            level = self.progress["global"]["total_level"]
        
        # Calculate XP needed for current level
        xp_for_current = 0
        for i in range(1, level):
            xp_for_current += (i + 1) * 100
        
        # XP needed for next level
        xp_for_next = xp_for_current + (level + 1) * 100
        
        # Progress within current level
        progress = (xp - xp_for_current) / (xp_for_next - xp_for_current) * 100
        
        return {
            "level": level,
            "xp": xp,
            "xp_current": xp_for_current,
            "xp_next": xp_for_next,
            "progress": min(progress, 100)
        }


# Global instance for easy import
# This will use session state when run in Streamlit
_gamification_instance = None

def get_gamification():
    """Get or create the global gamification instance."""
    global _gamification_instance
    if _gamification_instance is None:
        _gamification_instance = GamificationManager()
    return _gamification_instance

# For backward compatibility
gamification = get_gamification()
