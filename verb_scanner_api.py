# verb_scanner_api.py - Verb Conjugation Processor for Streamlit
"""Converted for Streamlit - Web-based verb conjugation fixing and processing"""

import json
import re
import os
import streamlit as st
from pathlib import Path

# ========== CONFIGURATION ==========
SEPARABLE_PREFIXES = [
    "ab", "an", "auf", "aus", "bei", "dar", "durch", "ein", "emp",
    "ent", "er", "fort", "ge", "heraus", "herein", "herum", "hin",
    "hinter", "los", "mit", "nach", "nieder", "vor", "weg", "weiter",
    "wieder", "zurück", "zusammen", "zu", "über", "unter", "um"
]

# Tenses where verbs should be separated (mostly finite forms)
TENSES_TO_SEPARATE = {
    "PRASENS", "PRATERITUM", 
    "KONJUNKTIV1_PRASENS", "KONJUNKTIV2_PRATERITUM"
}

# Tenses that should remain together (infinitives, participles)
TENSES_TO_KEEP_TOGETHER = {
    "FUTUR1", "FUTUR2", "PERFEKT", "PLUSQUAMPERFEKT",
    "KONJUNKTIV1_FUTUR1", "KONJUNKTIV1_PERFEKT",
    "KONJUNKTIV2_FUTUR1", "KONJUNKTIV2_FUTUR2"
}


# ========== HELPER FUNCTIONS ==========
def is_separable_verb(verb):
    """Check if a verb is separable based on common prefixes."""
    for prefix in SEPARABLE_PREFIXES:
        if verb.startswith(prefix) and len(verb) > len(prefix):
            # Check if it's not an inseparable prefix (some exceptions)
            if prefix not in ["be", "emp", "ent", "er", "ge", "ver", "zer"]:
                return True, prefix, verb[len(prefix):]
    return False, "", verb


def separate_verb_conjugation(conjugation_list, verb, tense):
    """
    Fix separable verb conjugations by moving the prefix to the end.
    Example: ["anzeige"] -> ["zeige", "an"]
    """
    if not conjugation_list:
        return conjugation_list
    
    is_separable, prefix, stem = is_separable_verb(verb)
    
    if not is_separable or tense not in TENSES_TO_SEPARATE:
        return conjugation_list
    
    fixed_conjugations = []
    
    for form in conjugation_list:
        if isinstance(form, str):
            # Check if the form contains the prefix
            if prefix and form.startswith(prefix):
                # Remove prefix and add it as separate word
                stem_form = form[len(prefix):]
                fixed_form = f"{stem_form} {prefix}"
            else:
                fixed_form = form
            fixed_conjugations.append(fixed_form)
        elif isinstance(form, list):
            # Handle nested lists (for multi-word forms)
            fixed_subforms = []
            for subform in form:
                if isinstance(subform, str) and prefix and subform.startswith(prefix):
                    stem_subform = subform[len(prefix):]
                    fixed_subforms.append(f"{stem_subform} {prefix}")
                else:
                    fixed_subforms.append(subform)
            fixed_conjugations.append(fixed_subforms)
        else:
            fixed_conjugations.append(form)
    
    return fixed_conjugations


def fix_participle_form(form, verb):
    """
    Check and fix participle forms for separable verbs.
    Example: "angezeigt" should remain as is for Perfekt tenses.
    """
    is_separable, prefix, stem = is_separable_verb(verb)
    
    if not is_separable:
        return form
    
    # For participles, the prefix should be at the beginning
    if isinstance(form, str) and form.startswith("ge"):
        # Check if it already has the prefix
        if not form.startswith(prefix):
            # It's already correct (prefix + ge + stem)
            return form
    
    return form


def load_translations(translation_file):
    """Load English translations from a JSON file."""
    if Path(translation_file).exists():
        with open(translation_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


# ========== MAIN PROCESSING FUNCTION ==========
def process_verbs(input_data, translation_data=None):
    """
    Process verb conjugations and fix separable verbs.
    Can accept either file path or JSON data.
    """
    # If input_data is a string, assume it's a file path
    if isinstance(input_data, str):
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return None, f"❌ Error: Input file '{input_data}' not found."
        except json.JSONDecodeError as e:
            return None, f"❌ Error: Invalid JSON: {e}"
    else:
        # Assume it's already JSON data
        data = input_data
    
    if not data:
        return None, "❌ No data to process"
    
    # Use translations if provided
    translations = translation_data or {}
    
    processed_data = {}
    fixed_count = 0
    skipped_verbs = []
    separable_verbs_found = []
    
    for verb, tenses_data in data.items():
        # Skip verbs that had errors in the original data
        if isinstance(tenses_data, dict) and "error" in tenses_data:
            skipped_verbs.append(verb)
            processed_data[verb] = tenses_data
            continue
        
        processed_verb_data = {}
        
        # Add English translation if available
        if verb in translations:
            processed_verb_data["English"] = translations[verb]
        else:
            processed_verb_data["English"] = f"to {verb}"
        
        # Process each tense
        for tense, conjugation_data in tenses_data.items():
            if conjugation_data is None:
                processed_verb_data[tense] = None
                continue
            
            fixed_tense_data = {}
            
            # Check if this is a separable verb
            is_separable, prefix, stem = is_separable_verb(verb)
            if is_separable and verb not in separable_verbs_found:
                separable_verbs_found.append(verb)
            
            for person, conjugation in conjugation_data.items():
                if isinstance(conjugation, list):
                    if tense in TENSES_TO_SEPARATE and is_separable:
                        # Fix separable verb forms
                        fixed_conjugation = separate_verb_conjugation(conjugation, verb, tense)
                        fixed_count += 1
                    elif tense in ["PERFEKT", "PLUSQUAMPERFEKT", "KONJUNKTIV1_PERFEKT"]:
                        # Fix participle forms for perfect tenses
                        fixed_conjugation = []
                        for i, form in enumerate(conjugation):
                            if i > 0:  # The participle is usually the second element
                                fixed_conjugation.append(fix_participle_form(form, verb))
                            else:
                                fixed_conjugation.append(form)
                    else:
                        fixed_conjugation = conjugation
                    
                    fixed_tense_data[person] = fixed_conjugation
                else:
                    fixed_tense_data[person] = conjugation
            
            processed_verb_data[tense] = fixed_tense_data
        
        processed_data[verb] = processed_verb_data
    
    return {
        "processed_data": processed_data,
        "fixed_count": fixed_count,
        "skipped_verbs": skipped_verbs,
        "separable_verbs_found": separable_verbs_found,
        "total_verbs": len(data)
    }, None


def create_translation_template(input_data):
    """Create a template for English translations."""
    # If input_data is a string, assume it's a file path
    if isinstance(input_data, str):
        try:
            with open(input_data, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            return None, "Could not load input file"
    else:
        data = input_data
    
    translation_template = {}
    
    for verb in data.keys():
        if isinstance(data[verb], dict) and "error" not in data[verb]:
            translation_template[verb] = f"to {verb}"
    
    return translation_template, f"Created template with {len(translation_template)} verbs"


# ---------- STREAMLIT UI ----------
def render_verb_scanner():
    """Render the Verb Scanner/Processor page in Streamlit."""
    
    st.title("🔧 Verb Conjugation Processor")
    st.markdown("Fix separable verb conjugations and add English translations")
    
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.subheader("⚙️ Settings")
        
        # Option to create translation template
        if st.button("📝 Create Translation Template", use_container_width=True):
            st.session_state.show_template = True
        
        st.divider()
        
        st.subheader("ℹ️ Info")
        st.caption(f"Separable prefixes: {', '.join(SEPARABLE_PREFIXES[:10])}...")
        st.caption(f"Tenses to separate: {', '.join(TENSES_TO_SEPARATE)}")
    
    # ---------- MAIN CONTENT ----------
    
    # Check if we have verb data in session state
    if 'verb_data' not in st.session_state:
        st.session_state.verb_data = None
    
    if 'processed_verb_data' not in st.session_state:
        st.session_state.processed_verb_data = None
    
    # ---------- FILE UPLOAD ----------
    st.subheader("📂 Upload Verb Data")
    
    uploaded_file = st.file_uploader(
        "Upload a JSON file with verb conjugations:",
        type=['json'],
        help="Upload a JSON file with German verb conjugations"
    )
    
    # Or use default file
    col1, col2 = st.columns(2)
    with col1:
        use_default = st.button("📖 Use Default File (data/german_verb_conjugations.json)", use_container_width=True)
    
    with col2:
        upload_translations = st.file_uploader(
            "📝 Upload Translations (optional):",
            type=['json'],
            help="Upload a JSON file with English translations"
        )
    
    # ---------- PROCESSING ----------
    if uploaded_file or use_default:
        
        # Load the data
        if use_default:
            try:
                with open("data/german_verb_conjugations.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                st.success("✅ Loaded default verb data")
            except:
                st.error("❌ Could not load default file. Please upload a file.")
                return
        else:
            try:
                data = json.load(uploaded_file)
                st.success(f"✅ Loaded {len(data)} verbs from uploaded file")
            except:
                st.error("❌ Invalid JSON file. Please check the format.")
                return
        
        # Load translations if uploaded
        translations = None
        if upload_translations:
            try:
                translations = json.load(upload_translations)
                st.success(f"✅ Loaded {len(translations)} translations")
            except:
                st.warning("⚠️ Invalid translations file. Using placeholders.")
        
        # Process button
        if st.button("🔄 Process Verbs", use_container_width=True, type="primary"):
            with st.spinner("Processing verbs..."):
                result, error = process_verbs(data, translations)
                
                if error:
                    st.error(error)
                else:
                    st.session_state.processed_verb_data = result
                    
                    # Show results
                    st.success("✅ Processing complete!")
                    
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Verbs", result["total_verbs"])
                    with col2:
                        st.metric("Separable Verbs", len(result["separable_verbs_found"]))
                    with col3:
                        st.metric("Fixed Conjugations", result["fixed_count"])
                    with col4:
                        st.metric("Skipped", len(result["skipped_verbs"]))
                    
                    # Show separable verbs
                    if result["separable_verbs_found"]:
                        with st.expander(f"🔗 Separable Verbs Found ({len(result['separable_verbs_found'])})"):
                            st.write(", ".join(result["separable_verbs_found"][:20]))
                            if len(result["separable_verbs_found"]) > 20:
                                st.write(f"... and {len(result['separable_verbs_found']) - 20} more")
                    
                    # Preview processed data
                    with st.expander("📋 Preview Processed Data"):
                        sample_verb = list(result["processed_data"].keys())[0] if result["processed_data"] else None
                        if sample_verb:
                            st.json({sample_verb: result["processed_data"][sample_verb]})
                    
                    # Download button
                    st.download_button(
                        label="💾 Download Processed JSON",
                        data=json.dumps(result["processed_data"], indent=2, ensure_ascii=False),
                        file_name="processed_verbs.json",
                        mime="application/json",
                        use_container_width=True
                    )
    
    # ---------- TRANSLATION TEMPLATE ----------
    if st.session_state.get('show_template', False):
        st.divider()
        st.subheader("📝 Translation Template")
        
        if uploaded_file or use_default:
            if use_default:
                try:
                    with open("data/german_verb_conjugations.json", 'r', encoding='utf-8') as f:
                        data = json.load(f)
                except:
                    st.error("Could not load data")
                    return
            else:
                try:
                    data = json.load(uploaded_file)
                except:
                    st.error("Could not load data")
                    return
            
            template, message = create_translation_template(data)
            if template:
                st.success(message)
                
                # Preview template
                st.json(dict(list(template.items())[:10]))
                if len(template) > 10:
                    st.caption(f"... and {len(template) - 10} more verbs")
                
                # Download template
                st.download_button(
                    label="💾 Download Translation Template",
                    data=json.dumps(template, indent=2, ensure_ascii=False),
                    file_name="english_translations_template.json",
                    mime="application/json",
                    use_container_width=True
                )
            
            # Reset template flag
            if st.button("Close Template", use_container_width=True):
                st.session_state.show_template = False
                st.rerun()
        else:
            st.info("Please upload or load verb data first.")
    
    # ---------- HELP SECTION ----------
    with st.expander("💡 How to Use"):
        st.markdown("""
        ### 1. Upload Data
        Upload a JSON file with German verb conjugations in the following format:
        ```json
        {
            "ansehen": {
                "PRASENS": {
                    "ich": ["sehe an"],
                    "du": ["siehst an"],
                    ...
                }
            }
        }
