# german_learning_app.py
import streamlit as st
import random
import webbrowser
import xlrd
import os
import sys

# ---------- RESOURCE PATH (for deployment) ----------
def resource_path(relative_path):
    """Get absolute path to resource, works for dev and deployment"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- LOAD DATA ----------
@st.cache_resource
def load_workbook():
    """Load the Excel workbook - cached as resource (not serialized)"""
    return xlrd.open_workbook(resource_path("prefixes.xls"))

@st.cache_data
def load_text_files():
    """Load text files - these are pickle-serializable"""
    # Load verbs and meanings
    verbs = []
    meaninglist = []
    with open(resource_path("plain.txt"), "r", encoding="utf-8") as file:
        for l in file:
            if l[0] != "[" and len(l) > 1:
                verbs.append(l.split(":")[0])
                meaninglist.append([])
            if l[0] == "[":
                meaninglist[len(meaninglist)-1].append(l.strip())
    
    # Load prefix meanings
    prefixNames = []
    prefixMeanings = []
    with open(resource_path("prefixes.txt"), "r", encoding="utf-8") as file2:
        for l in file2:
            if l[0] != "[":
                l = l.split(":")[0]
                prefixNames.append(l)
                prefixMeanings.append([])
            else:
                prefixMeanings[len(prefixMeanings)-1].append(l.strip())
    
    return verbs, meaninglist, prefixNames, prefixMeanings

# Load data
workbook = load_workbook()
worksheet = workbook.sheet_by_index(0)
verbs, meaninglist, prefixNames, prefixMeanings = load_text_files()

# ---------- SESSION STATE INITIALIZATION ----------
if 'x' not in st.session_state:
    st.session_state.x = random.randint(1, 82)
    st.session_state.y = random.randint(1, 30)
    st.session_state.prefix = worksheet.cell_value(0, st.session_state.y)
    st.session_state.verb = worksheet.cell_value(st.session_state.x, 0)
    st.session_state.feedback = ""
    st.session_state.feedback_color = "green"
    st.session_state.show_second_question = False
    st.session_state.threeMeanings = []
    st.session_state.trueNumberForChoiceQ2 = 0
    st.session_state.has_meaning_options = False
    st.session_state.show_meaning_display = False
    st.session_state.question1_answered = False
    st.session_state.quiz_complete = False

# ---------- HELPER FUNCTIONS ----------
def get_prefix_meaning_message(prefix):
    """Get meaning message for a prefix"""
    if prefix in prefixNames:
        idx = prefixNames.index(prefix)
        message = prefix + ":\n"
        for meaning in prefixMeanings[idx]:
            message += meaning + "\n"
        return message
    return "No meaning found"

def generate_new_words():
    """Generate new random prefix and verb"""
    # Reset states
    st.session_state.x = random.randint(1, 82)
    st.session_state.y = random.randint(1, 30)
    st.session_state.prefix = worksheet.cell_value(0, st.session_state.y)
    st.session_state.verb = worksheet.cell_value(st.session_state.x, 0)
    st.session_state.feedback = ""
    st.session_state.feedback_color = "green"
    st.session_state.show_second_question = False
    st.session_state.question1_answered = False
    st.session_state.quiz_complete = False
    st.session_state.show_meaning_display = False
    
    # Generate meaning options for second question
    prefix_verb = st.session_state.prefix + st.session_state.verb
    
    if prefix_verb in verbs:
        st.session_state.has_meaning_options = True
        num = verbs.index(prefix_verb)
        
        # Get correct meaning
        correct_meaning = meaninglist[num][random.randint(0, len(meaninglist[num])-1)]
        
        # Get two wrong meanings
        wrong_meanings = []
        attempts = 0
        while len(wrong_meanings) < 2 and attempts < 100:
            random_num = random.randint(0, len(meaninglist)-1)
            if random_num != num and len(meaninglist[random_num]) > 0:
                wrong_meaning = meaninglist[random_num][random.randint(0, len(meaninglist[random_num])-1)]
                if wrong_meaning not in wrong_meanings and wrong_meaning != correct_meaning:
                    wrong_meanings.append(wrong_meaning)
            attempts += 1
        
        # If we couldn't find enough wrong meanings, use placeholders
        while len(wrong_meanings) < 2:
            wrong_meanings.append("[No meaning available]")
        
        # Create shuffled list
        threeMeanings = [correct_meaning] + wrong_meanings
        random.shuffle(threeMeanings)
        
        st.session_state.threeMeanings = threeMeanings
        st.session_state.trueNumberForChoiceQ2 = threeMeanings.index(correct_meaning) + 1
    else:
        st.session_state.has_meaning_options = False
        st.session_state.threeMeanings = []
        st.session_state.trueNumberForChoiceQ2 = 0

def check_question1(answer):
    """Check if the word exists"""
    selection = worksheet.cell_value(st.session_state.x, st.session_state.y)
    st.session_state.question1_answered = True
    
    if selection != "" and answer == "Yes":
        st.session_state.feedback = "✓ Correct! The word exists."
        st.session_state.feedback_color = "green"
        # Show second question if meaning options exist
        if st.session_state.has_meaning_options:
            st.session_state.show_second_question = True
    elif selection == "" and answer == "No":
        st.session_state.feedback = "✓ Correct! The word does not exist."
        st.session_state.feedback_color = "green"
        st.session_state.show_second_question = False
    else:
        if selection != "":
            st.session_state.feedback = "✗ Wrong! The word actually exists."
        else:
            st.session_state.feedback = "✗ Wrong! The word does not exist."
        st.session_state.feedback_color = "red"
        st.session_state.show_second_question = False

def check_question2(answer_number):
    """Check the meaning selection"""
    if answer_number == st.session_state.trueNumberForChoiceQ2:
        text = "✓ Correct meaning!\n\n"
        prefix_verb = st.session_state.prefix + st.session_state.verb
        if prefix_verb in verbs:
            num = verbs.index(prefix_verb)
            for meaning in meaninglist[num]:
                text += meaning + "\n"
        st.session_state.feedback = text
        st.session_state.feedback_color = "green"
        st.session_state.quiz_complete = True
    else:
        text = "✗ Wrong meaning.\n\n"
        prefix_verb = st.session_state.prefix + st.session_state.verb
        if prefix_verb in verbs:
            num = verbs.index(prefix_verb)
            text += "The correct meaning is:\n"
            for meaning in meaninglist[num]:
                text += meaning + "\n"
        st.session_state.feedback = text
        st.session_state.feedback_color = "red"
        st.session_state.quiz_complete = True

def toggle_meaning_display():
    st.session_state.show_meaning_display = not st.session_state.show_meaning_display

# ---------- UI ----------
st.set_page_config(page_title="🇩🇪 German Learning Tool", page_icon="🇩🇪", layout="centered")

# Title
st.title("🇩🇪 German Prefix + Verb Learning Tool")

# Initialize new words if needed
if 'initialized' not in st.session_state:
    generate_new_words()
    st.session_state.initialized = True

# ---------- MAIN DISPLAY ----------
# Display prefix (clickable for meaning)
prefix_meaning = get_prefix_meaning_message(st.session_state.prefix)
prefix_col1, prefix_col2 = st.columns([3, 1])
with prefix_col1:
    st.markdown(f"### **<span style='color:red'>{st.session_state.prefix}</span>**", unsafe_allow_html=True)
with prefix_col2:
    if st.button("📖 Show meaning", key="show_meaning"):
        toggle_meaning_display()

# Show prefix meaning if toggled
if st.session_state.show_meaning_display:
    st.info(prefix_meaning)

# Display verb
st.markdown(f"### **{st.session_state.verb}**")

# Separator
st.divider()

# ---------- QUESTION 1 ----------
st.subheader("Does this word exist?")
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Yes", key="q1_yes", use_container_width=True):
        if not st.session_state.question1_answered:
            check_question1("Yes")
        else:
            st.warning("Already answered! Generate new words for another round.")

with col2:
    if st.button("❌ No", key="q1_no", use_container_width=True):
        if not st.session_state.question1_answered:
            check_question1("No")
        else:
            st.warning("Already answered! Generate new words for another round.")

# ---------- QUESTION 2 ----------
if st.session_state.show_second_question:
    st.divider()
    st.subheader("What could it mean?")
    
    # Display meaning options
    meanings = st.session_state.threeMeanings
    if len(meanings) >= 3:
        cols = st.columns(3)
        for i, meaning in enumerate(meanings):
            with cols[i]:
                if st.button(f"{i+1}. {meaning}", key=f"q2_{i}", use_container_width=True):
                    if not st.session_state.quiz_complete:
                        check_question2(i+1)
                    else:
                        st.warning("Already answered! Generate new words for another round.")

# ---------- FEEDBACK ----------
if st.session_state.feedback:
    color = st.session_state.feedback_color
    if color == "green":
        st.success(st.session_state.feedback)
    else:
        st.error(st.session_state.feedback)

# ---------- BUTTONS ----------
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Generate new words", use_container_width=True):
        generate_new_words()
        st.rerun()

with col2:
    prefix_verb = st.session_state.prefix + st.session_state.verb
    wiktionary_url = f"https://de.wiktionary.org/wiki/{prefix_verb}"
    st.markdown(f'<a href="{wiktionary_url}" target="_blank"><button style="width:100%; padding:0.5rem;">📚 See more on Wiktionary</button></a>', unsafe_allow_html=True)

# ---------- FOOTER ----------
st.caption("💡 Click the prefix to see its meanings • Answer both questions to learn effectively!")