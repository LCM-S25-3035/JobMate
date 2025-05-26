import streamlit as st
import ast
import os

def parse_options(options_str):
    try:
        return ast.literal_eval(options_str) if options_str else []
    except Exception:
        return []

def simplify_type(raw_type):
    raw_type = raw_type.lower()
    if 'boolean' in raw_type:
        return 'select' #want the dropdown instead
    if 'select' in raw_type:
        return 'select'
    if 'date' in raw_type:
        return 'date'
    return 'text'

def render_text_input(label, default_value, key):
    return st.text_input(label, value=default_value, key=key)

def render_selectbox(label, options, default_value, key):
    index = options.index(default_value) if default_value in options else 0
    return st.selectbox(label, options, index=index, key=key)

def render_boolean(label, default_value, key):
    options = ["Yes", "No"]
    index = options.index(default_value) if default_value in options else 0
    return st.radio(label, options=options, index=index, key=key)

def render_date(label, default_value, key):
    import datetime
    if default_value:
        try:
            default_date = datetime.datetime.strptime(default_value, "%Y-%m-%d").date()
        except Exception:
            default_date = None
    else:
        default_date = None
    return st.date_input(label, value=default_date or datetime.date.today(), key=key)

def render_question(q: dict, default_value):
    label = f"{q.get('question_text', 'Question')}{' *' if q.get('required', 'FALSE').upper() == 'TRUE' else ''}"
    raw_type = q.get('type', 'text')
    options_str = q.get('options (if applicable)', '')

    qtype = simplify_type(raw_type)
    options = parse_options(options_str)
    key = q.get('question_id')

    renderers = {
        'text': lambda: render_text_input(label, default_value, key),
        'select': lambda: render_selectbox(label, options, default_value, key),
        'boolean': lambda: render_boolean(label, default_value, key),
        'date': lambda: render_date(label, default_value, key)
    }

    return renderers.get(qtype, render_text_input)()

def load_css(file_path: str):
    if not os.path.exists(file_path):
        st.error(f"CSS file not found: {file_path}")
        return

    with open(file_path) as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# OpenAI 4o, Last Prompt:
# i want to have a funcitonality where i can define all the things that 
# ui need to control like input fields, dropdown boxes, date pickers. 
# can explain the strategy first? 

# OpenAI 4o, First Prompt:
# Cognitive Complexity of functions should not be too high (python:S3776) why am i seeing this for render_question function? 