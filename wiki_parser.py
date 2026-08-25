# wiki_parser.py - German Dictionary Parser for Streamlit
"""Converted for Streamlit - Web-based dictionary JSONL parser with filtering and export"""

import streamlit as st
import json
import os
import pandas as pd
from io import StringIO

class WikiParser:
    """Parse German dictionary JSONL files and extract word information."""
    
    def __init__(self):
        self.words = []
        self.stats = {
            "total": 0,
            "with_etymology": 0,
            "with_senses": 0,
            "with_links": 0,
            "with_antonyms": 0,
            "with_synonyms": 0
        }
    
    def parse_line(self, line):
        """Parse a single JSONL line and extract word information."""
        try:
            word_entry = json.loads(line)
        except json.JSONDecodeError:
            return None
        
        # Safely get the word
        word = word_entry.get('word', 'N/A')
        
        # Safely get etymology
        etymology = word_entry.get('etymology_text', '')
        
        # Safely get meanings
        senses = word_entry.get('senses', [])
        
        word_data = {
            'word': word,
            'etymology': etymology,
            'senses': []
        }
        
        if senses:
            # Process each sense
            for sense in senses:
                sense_data = {
                    'links': [],
                    'antonyms': [],
                    'synonyms': [],
                    'raw_data': sense
                }
                
                # Safely get links
                links = sense.get('links', [])
                if links:
                    for link in links:
                        if isinstance(link, dict):
                            link_word = link.get('word', 'Unnamed link')
                            sense_data['links'].append(link_word)
                        elif isinstance(link, str):
                            sense_data['links'].append(link)
                        elif isinstance(link, list) and link:
                            sense_data['links'].append(str(link[0]))
                        else:
                            sense_data['links'].append(str(link))
                
                # Safely get antonyms
                antonyms = sense.get('antonyms', [])
                if antonyms:
                    for ant in antonyms:
                        if isinstance(ant, dict):
                            sense_data['antonyms'].append(ant.get('word', 'Unnamed antonym'))
                        elif isinstance(ant, str):
                            sense_data['antonyms'].append(ant)
                        elif isinstance(ant, list) and ant:
                            sense_data['antonyms'].append(str(ant[0]))
                        else:
                            sense_data['antonyms'].append(str(ant))
                
                # Safely get synonyms
                synonyms = sense.get('synonyms', [])
                if synonyms:
                    for syn in synonyms:
                        if isinstance(syn, dict):
                            sense_data['synonyms'].append(syn.get('word', 'Unnamed synonym'))
                        elif isinstance(syn, str):
                            sense_data['synonyms'].append(syn)
                        elif isinstance(syn, list) and syn:
                            sense_data['synonyms'].append(str(syn[0]))
                        else:
                            sense_data['synonyms'].append(str(syn))
                
                word_data['senses'].append(sense_data)
        
        return word_data
    
    def parse_file(self, file_content, max_lines=100):
        """Parse a JSONL file content and extract word information."""
        self.words = []
        self.stats = {
            "total": 0,
            "with_etymology": 0,
            "with_senses": 0,
            "with_links": 0,
            "with_antonyms": 0,
            "with_synonyms": 0
        }
        
        lines = file_content.split('\n')
        processed = 0
        
        for line in lines:
            if not line.strip():
                continue
            
            if processed >= max_lines:
                break
            
            word_data = self.parse_line(line)
            if word_data:
                self.words.append(word_data)
                self.stats["total"] += 1
                
                if word_data.get('etymology'):
                    self.stats["with_etymology"] += 1
                
                if word_data.get('senses'):
                    self.stats["with_senses"] += 1
                    
                    for sense in word_data['senses']:
                        if sense.get('links'):
                            self.stats["with_links"] += 1
                        if sense.get('antonyms'):
                            self.stats["with_antonyms"] += 1
                        if sense.get('synonyms'):
                            self.stats["with_synonyms"] += 1
            
            processed += 1
        
        return self.words
    
    def to_dataframe(self):
        """Convert parsed words to a pandas DataFrame."""
        rows = []
        for word_data in self.words:
            word = word_data['word']
            etymology = word_data.get('etymology', '')
            
            if word_data.get('senses'):
                for i, sense in enumerate(word_data['senses']):
                    row = {
                        'word': word,
                        'sense': i + 1,
                        'etymology': etymology if i == 0 else '',
                        'links': ', '.join(sense.get('links', [])),
                        'antonyms': ', '.join(sense.get('antonyms', [])),
                        'synonyms': ', '.join(sense.get('synonyms', []))
                    }
                    rows.append(row)
            else:
                rows.append({
                    'word': word,
                    'sense': 0,
                    'etymology': etymology,
                    'links': '',
                    'antonyms': '',
                    'synonyms': ''
                })
        
        return pd.DataFrame(rows)
    
    def search(self, search_term):
        """Search for words containing the search term."""
        search_term = search_term.lower().strip()
        results = []
        
        for word_data in self.words:
            word = word_data['word'].lower()
            if search_term in word:
                results.append(word_data)
            else:
                # Search in links, antonyms, synonyms
                for sense in word_data.get('senses', []):
                    for link in sense.get('links', []):
                        if search_term in link.lower():
                            results.append(word_data)
                            break
                    if word_data in results:
                        break
        
        return results
    
    def get_stats(self):
        """Get parsing statistics."""
        return self.stats


# ---------- STREAMLIT UI ----------
def render_wiki_parser():
    """Render the Wiki Parser page in Streamlit."""
    
    st.title("📚 German Dictionary Parser")
    st.markdown("Parse and explore German dictionary data from JSONL files")
    
    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.subheader("⚙️ Settings")
        
        max_lines = st.slider(
            "Max lines to parse:",
            min_value=10,
            max_value=1000,
            value=100,
            step=10,
            help="Limit the number of lines parsed for performance"
        )
        
        st.divider()
        
        st.subheader("📊 Statistics")
        stats_placeholder = st.empty()
    
    # ---------- MAIN CONTENT ----------
    
    # Initialize parser in session state
    if 'wiki_parser' not in st.session_state:
        st.session_state.wiki_parser = WikiParser()
    
    if 'wiki_parsed_words' not in st.session_state:
        st.session_state.wiki_parsed_words = []
    
    parser = st.session_state.wiki_parser
    
    # ---------- FILE UPLOAD ----------
    st.subheader("📂 Upload Dictionary File")
    
    uploaded_file = st.file_uploader(
        "Upload a JSONL file (kaikki.org-dictionary-German.jsonl):",
        type=['jsonl', 'txt'],
        help="Upload the dictionary file in JSONL format"
    )
    
    # Or use default file
    col1, col2 = st.columns(2)
    with col1:
        use_default = st.button("📖 Use Default File", use_container_width=True)
    
    with col2:
        # Load sample data
        load_sample = st.button("📋 Load Sample Data", use_container_width=True)
    
    # ---------- LOAD DEFAULT FILE ----------
    if use_default:
        try:
            with open("kaikki.org-dictionary-German.jsonl", 'r', encoding='utf-8') as f:
                content = f.read()
            
            with st.spinner(f"Parsing {max_lines} lines..."):
                words = parser.parse_file(content, max_lines)
                st.session_state.wiki_parsed_words = words
            
            st.success(f"✅ Parsed {len(words)} words from default file!")
            st.rerun()
            
        except FileNotFoundError:
            st.error("❌ Default file 'kaikki.org-dictionary-German.jsonl' not found.")
            st.info("Please upload a file or use the sample data.")
        except Exception as e:
            st.error(f"❌ Error loading default file: {e}")
    
    # ---------- LOAD SAMPLE DATA ----------
    if load_sample:
        # Create sample data from the script's example
        sample_lines = [
            '{"word": "Haus", "etymology_text": "From Old High German hūs", "senses": [{"links": ["building", "house"], "antonyms": ["Draußen"], "synonyms": ["Gebäude"]}]}',
            '{"word": "Auto", "etymology_text": "From Greek autos", "senses": [{"links": ["vehicle", "car"], "antonyms": ["Fahrrad"], "synonyms": ["PKW"]}]}',
            '{"word": "Essen", "etymology_text": "From Old High German ezzan", "senses": [{"links": ["food", "meal"], "antonyms": ["Trinken"], "synonyms": ["Nahrung"]}]}',
            '{"word": "Trinken", "etymology_text": "From Old High German trinkan", "senses": [{"links": ["beverage", "drink"], "antonyms": ["Essen"], "synonyms": ["Schlucken"]}]}',
            '{"word": "Schlafen", "etymology_text": "From Old High German slāfan", "senses": [{"links": ["sleep", "rest"], "antonyms": ["Wachen"], "synonyms": ["Ruhen"]}]}'
        ]
        
        with st.spinner("Loading sample data..."):
            sample_content = '\n'.join(sample_lines)
            words = parser.parse_file(sample_content, max_lines)
            st.session_state.wiki_parsed_words = words
        
        st.success(f"✅ Loaded {len(words)} sample words!")
        st.rerun()
    
    # ---------- PROCESS UPLOADED FILE ----------
    if uploaded_file:
        try:
            content = uploaded_file.read().decode('utf-8')
            
            if st.button("🔄 Parse File", use_container_width=True, type="primary"):
                with st.spinner(f"Parsing {max_lines} lines..."):
                    words = parser.parse_file(content, max_lines)
                    st.session_state.wiki_parsed_words = words
                
                st.success(f"✅ Parsed {len(words)} words from uploaded file!")
                st.rerun()
                
        except Exception as e:
            st.error(f"❌ Error parsing file: {e}")
    
    # ---------- DISPLAY PARSED DATA ----------
    if st.session_state.wiki_parsed_words:
        words = st.session_state.wiki_parsed_words
        stats = parser.get_stats()
        
        # Update stats in sidebar
        with stats_placeholder.container():
            st.metric("Total Words", stats["total"])
            st.metric("With Etymology", stats["with_etymology"])
            st.metric("With Senses", stats["with_senses"])
            st.metric("With Links", stats["with_links"])
            st.metric("With Antonyms", stats["with_antonyms"])
            st.metric("With Synonyms", stats["with_synonyms"])
        
        # ---------- SEARCH ----------
        st.divider()
        st.subheader("🔍 Search Parsed Words")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            search_term = st.text_input(
                "Search for a word or related term:",
                placeholder="e.g., Haus, building, sleep..."
            )
        with col2:
            st.write("")
            st.write("")
            if st.button("🔍 Search", use_container_width=True):
                if search_term:
                    results = parser.search(search_term)
                    st.session_state.wiki_search_results = results
                    st.rerun()
        
        # ---------- DISPLAY WORDS ----------
        st.divider()
        st.subheader(f"📖 Parsed Words ({len(words)})")
        
        # Display as table or cards
        view_mode = st.radio("View Mode:", ["Table", "Cards"], horizontal=True)
        
        if view_mode == "Table":
            # Convert to DataFrame
            df = parser.to_dataframe()
            st.dataframe(df, use_container_width=True, height=400)
            
            # Download button
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download as CSV",
                data=csv,
                file_name="parsed_words.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        else:  # Cards view
            # Display search results or all words
            display_words = st.session_state.get('wiki_search_results', words)
            
            if st.session_state.get('wiki_search_results'):
                st.info(f"Showing {len(display_words)} search results")
                # Clear search results after display
                if st.button("Clear Search Results", use_container_width=True):
                    st.session_state.wiki_search_results = None
                    st.rerun()
            
            for word_data in display_words:
                with st.container(border=True):
                    st.markdown(f"### {word_data['word']}")
                    
                    if word_data.get('etymology'):
                        st.markdown(f"**Etymology:** {word_data['etymology']}")
                    
                    senses = word_data.get('senses', [])
                    if senses:
                        for i, sense in enumerate(senses):
                            st.markdown(f"**Sense {i+1}:**")
                            
                            if sense.get('links'):
                                st.markdown(f"  • **Links:** {', '.join(sense['links'])}")
                            if sense.get('antonyms'):
                                st.markdown(f"  • **Antonyms:** {', '.join(sense['antonyms'])}")
                            if sense.get('synonyms'):
                                st.markdown(f"  • **Synonyms:** {', '.join(sense['synonyms'])}")
                    else:
                        st.caption("No meanings available")
        
        # ---------- EXPORT ----------
        st.divider()
        st.subheader("📤 Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export as JSON
            json_data = json.dumps(words, indent=2, ensure_ascii=False)
            st.download_button(
                label="💾 Download as JSON",
                data=json_data,
                file_name="parsed_words.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # Export as CSV
            df = parser.to_dataframe()
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download as CSV",
                data=csv,
                file_name="parsed_words.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    else:
        st.info("👈 Upload a JSONL file, use the default file, or load sample data to get started.")
        
        # Show expected format
        with st.expander("📋 Expected File Format"):
            st.markdown("""
            The parser expects a JSONL (JSON Lines) file with each line containing a JSON object like:
            
            ```json
            {
                "word": "Haus",
                "etymology_text": "From Old High German hūs",
                "senses": [
                    {
                        "links": ["building", "house"],
                        "antonyms": ["Draußen"],
                        "synonyms": ["Gebäude"]
                    }
                ]
            }
