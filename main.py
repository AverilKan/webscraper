'main.py: A Streamlit app to scrape a website and parse the DOM content with LLM.'

import streamlit as st
from scrape import scrape_website, extract_body_content, clean_body_content, split_content
from parse import parse  # Now dynamically structures data

st.title('🔍 Web Scraping with AI')

if "dom_content" not in st.session_state:
    st.session_state.dom_content = ""

url = st.text_input('Enter URL:')

if st.button('Scrape site'):
    st.write(f'🕵️ Scraping website: {url}...')

    result = scrape_website(url)
    if result:
        body_content = extract_body_content(result)
        clean_content = clean_body_content(body_content)

        st.session_state.dom_content = clean_content  

        with st.expander('Show Extracted Content'):
            st.text_area('Extracted DOM Content:', value=clean_content, height=300)

if st.session_state.dom_content:
    if st.button('Parse content'):
        st.write('📝 Parsing content with AI...')
        
        dom_chunks = split_content(st.session_state.dom_content)
        parsed_df = parse(dom_chunks)  # Fully automated!

        with st.expander('Show Parsed Data'):
            st.dataframe(parsed_df)








