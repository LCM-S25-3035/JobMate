import os
import streamlit as st

def load_css(file_path: str):
    if not os.path.exists(file_path):
        st.error(f"CSS file not found: {file_path}")
        return

    with open(file_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)