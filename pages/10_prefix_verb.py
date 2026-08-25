# pages/10_prefix_verb.py
import streamlit as st
import random
import os
import sys
import xlrd

st.set_page_config(
    page_title="🇩🇪 Prefix + Verb - German Learning",
    page_icon="🇩🇪",
    layout="centered"
)

# ---------- RESOURCE PATH ----------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ---------- LOAD DATA ----------
@st.cache_resource
def load_workbook():
    return xlrd.open_workbook(resource_path("data/prefixes.xls"))

@st.cache_data
def load_text_files():
    verbs = []
    meaninglist = []
    
    # Load verbs and meanings
    try:
        with open(resource_path("data/plain.txt"), "r", encoding="utf-8") as file:
            for l in file:
                if l[0] != "[" and len(l) > 1:
                    verbs.append(l.split(":")[0])
                    meaninglist.append([])
                if l[0] == "[":
                    meaninglist[len(meaninglist)-1].append(l.strip())
    except FileNotFoundError:
        st.warning("⚠️ plain.txt not found. Using fallback data.")
        return [], []
    
    # Load prefix meanings
    prefixNames = []
    prefixMeanings = []
    try:
        with open(resource_path("data/prefixes.txt"), "r", encoding="utf-8") as file2:
            for l in file2:
                if l[0] != "[":
                    l = l.split(":")[0]
                    prefixNames.append(l)
                    prefixMeanings.append([])
                else:
                    prefixMeanings[len(prefixMeanings)-1].append(l.strip())
    except FileNotFoundError:
        st.warning("⚠️ prefixes.txt not found. Using fallback data.")
        return verbs, meaninglist, [], []
    
    return verbs, meaninglist, prefixNames, prefixMeanings

# ---------- LOAD DATA ----------
try:
    workbook = load_workbook()
    worksheet = workbook.sheet_by_index(0)
    verbs, meaninglist, prefixNames, prefixMeanings = load_text_files()
    data_loaded = True
except Exception as e:
    data_loaded = False
    st.error(f"❌ Error loading data: {e}")
    st.info("💡 Please make sure these files exist in the data/ folder:\n- prefixes.xls\n- plain.txt\n- prefixes.txt")

# ---------- SESSION STATE ----------
if data_loaded:
    if 'pv_x' not in st.session_state:
        st.session_state.pv_x = random.randint(1, 82)
        st.session_state.pv_y = random.randint(1, 30)
        st.session_state.pv_prefix = worksheet.cell_value(0, st.session_state.pv_y)
        st.session_state.pv_verb = worksheet.cell_value(st.session_state.pv_x, 0)
        st.session_state.pv_feedback = ""
        st.session_state.pv_feedback_color = "green"
        st.session_state.pv_show_second = False
        st.session_state.pv_threeMeanings = []
        st.session_state.pv_trueNumber = 0
        st.session_state.pv_has_options = False
        st.session_state.pv_show_meaning = False
        st.session_state.pv_q1_answered = False
        st.session_state.pv_quiz_complete = False
        st.session_state.pv_initialized = True

# ---------- HELPER FUNCTIONS ----------
def get_prefix_meaning_message(prefix):
    if prefix in prefixNames:
        idx = prefixNames.index(prefix)
        message = prefix + ":\n" + "\n".join(prefixMeanings[idx])
        return message
    return "No meaning found"

def generate_new_words():
    st.session_state.pv_x = random.randint(1, 82)
    st.session_state.pv_y = random.randint(1, 30)
    st.session_state.pv_prefix = worksheet.cell_value(0, st.session_state.pv_y)
    st.session_state.pv_verb = worksheet.cell_value(st.session_state.pv_x, 0)
    st.session_state.pv_feedback = ""
    st.session_state.pv_feedback_color = "green"
    st.session_state.pv_show_second = False
    st.session_state.pv_q1_answered = False
    st.session_state.pv_quiz_complete = False
    st.session_state.pv_show_meaning = False
    
    prefix_verb = st.session_state.pv_prefix + st.session_state.pv_verb
    
    if prefix_verb in verbs:
        st.session_state.pv_has_options = True
        num = verbs.index(prefix_verb)
        
        correct_meaning = meaninglist[num][random.randint(0, len(meaninglist[num])-1)]
        
        wrong_meanings = []
        attempts = 0
        while len(wrong_meanings) < 2 and attempts < 100:
            random_num = random.randint(0, len(meaninglist)-1)
            if random_num != num and len(meaninglist[random_num]) > 0:
                wrong_meaning = meaninglist[random_num][random.randint(0, len(meaninglist[random_num])-1)]
                if wrong_meaning not in wrong_meanings and wrong_meaning != correct_meaning:
                    wrong_meanings.append(wrong_meaning)
            attempts += 1
        
        while len(wrong_meanings) < 2:
            wrong_meanings.append("[No meaning available]")
        
        threeMeanings = [correct_meaning] + wrong_meanings
        random.shuffle(threeMeanings)
        
        st.session_state.pv_threeMeanings = threeMeanings
        st.session_state.pv_trueNumber = threeMeanings.index(correct_meaning) + 1
    else:
        st.session_state.pv_has_options = False
        st.session_state.pv_threeMeanings = []
        st.session_state.pv_trueNumber = 0

def check_question1(answer):
    selection = worksheet.cell_value(st.session_state.pv_x, st.session_state.pv_y)
    st.session_state.pv_q1_answered = True
    
    if selection != "" and answer == "Yes":
        st.session_state.pv_feedback = "✓ Correct! The word exists."
        st.session_state.pv_feedback_color = "green"
        if st.session_state.pv_has_options:
            st.session_state.pv_show_second = True
    elif selection == "" and answer == "No":
        st.session_state.pv_feedback = "✓ Correct! The word does not exist."
        st.session_state.pv_feedback_color = "green"
        st.session_state.pv_show_second = False
    else:
        if selection != "":
            st.session_state.pv_feedback = "✗ Wrong! The word actually exists."
        else:
            st.session_state.pv_feedback = "✗ Wrong! The word does not exist."
        st.session_state.pv_feedback_color = "red"
        st.session_state.pv_show_second = False

def check_question2(answer_number):
    if answer_number == st.session_state.pv_trueNumber:
        text = "✓ Correct meaning!\n\n"
        prefix_verb = st.session_state.pv_prefix + st.session_state.pv_verb
        if prefix_verb in verbs:
            num = verbs.index(prefix_verb)
            for meaning in meaninglist[num]:
                text += meaning + "\n"
        st.session_state.pv_feedback = text
        st.session_state.pv_feedback_color = "green"
        st.session_state.pv_quiz_complete = True
    else:
        text = "✗ Wrong meaning.\n\n"
        prefix_verb = st.session_state.pv_prefix + st.session_state.pv_verb
        if prefix_verb in verbs:
            num = verbs.index(prefix_verb)
            text += "The correct meaning is:\n"
            for meaning in meaninglist[num]:
                text += meaning + "\n"
        st.session_state.pv_feedback = text
        st.session_state.pv_feedback_color = "red"
        st.session_state.pv_quiz_complete = True

def toggle_meaning_display():
    st.session_state.pv_show_meaning = not st.session_state.pv_show_meaning

# ---------- UI ----------
if not data_loaded:
    st.stop()

st.title("🇩🇪 German Prefix + Verb Tool")
st.markdown("Learn German prefixes and their verb combinations!")

# ---------- MAIN DISPLAY ----------
prefix_meaning = get_prefix_meaning_message(st.session_state.pv_prefix)

col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"### **<span style='color:red'>{st.session_state.pv_prefix}</span>**", unsafe_allow_html=True)
with col2:
    if st.button("📖 Show meaning", key="pv_show_meaning"):
        toggle_meaning_display()

if st.session_state.pv_show_meaning:
    st.info(prefix_meaning)

st.markdown(f"### **{st.session_state.pv_verb}**")
st.divider()

# ---------- QUESTION 1 ----------
st.subheader("Does this word exist?")
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Yes", key="pv_q1_yes", use_container_width=True):
        if not st.session_state.pv_q1_answered:
            check_question1("Yes")
        else:
            st.warning("Already answered! Generate new words.")

with col2:
    if st.button("❌ No", key="pv_q1_no", use_container_width=True):
        if not st.session_state.pv_q1_answered:
            check_question1("No")
        else:
            st.warning("Already answered! Generate new words.")

# ---------- QUESTION 2 ----------
if st.session_state.pv_show_second:
    st.divider()
    st.subheader("What could it mean?")
    
    meanings = st.session_state.pv_threeMeanings
    if len(meanings) >= 3:
        cols = st.columns(3)
        for i, meaning in enumerate(meanings):
            with cols[i]:
                if st.button(f"{i+1}. {meaning}", key=f"pv_q2_{i}", use_container_width=True):
                    if not st.session_state.pv_quiz_complete:
                        check_question2(i+1)
                    else:
                        st.warning("Already answered! Generate new words.")

# ---------- FEEDBACK ----------
if st.session_state.pv_feedback:
    if st.session_state.pv_feedback_color == "green":
        st.success(st.session_state.pv_feedback)
    else:
        st.error(st.session_state.pv_feedback)

# ---------- BUTTONS ----------
st.divider()

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Generate new words", use_container_width=True):
        generate_new_words()
        st.rerun()

with col2:
    prefix_verb = st.session_state.pv_prefix + st.session_state.pv_verb
    wiktionary_url = f"https://de.wiktionary.org/wiki/{prefix_verb}"
    st.markdown(f'<a href="{wiktionary_url}" target="_blank"><button style="width:100%; padding:0.5rem;">📚 See more on Wiktionary</button></a>', unsafe_allow_html=True)

st.caption("💡 Click the prefix to see its meanings • Answer both questions to learn effectively!")
