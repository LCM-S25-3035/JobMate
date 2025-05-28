import streamlit as st

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

    today = datetime.date.today()

    if default_value:
        try:
            if isinstance(default_value, str):
                default_date = datetime.datetime.strptime(default_value, "%Y-%m-%d").date()
            elif isinstance(default_value, datetime.datetime):
                default_date = default_value.date()
            elif isinstance(default_value, datetime.date):
                default_date = default_value
            else:
                default_date = datetime.date(1990, 1, 1)
        except Exception:
            default_date = datetime.date(1990, 1, 1)
    else:
        default_date = datetime.date(1990, 1, 1)

    return st.date_input(label, value=default_date, min_value=datetime.date(1900, 1, 1), max_value=today, key=key)

def render_question(q: dict, default_value):
    label = f"{q.get('question_text', 'Question')}{' *' if q.get('required', 'FALSE').upper() == 'TRUE' else ''}"
    raw_type = q.get('type', 'text')
    options = q.get('options', [])
    qtype = simplify_type(raw_type)
    key = q.get('question_id')

    renderers = {
        'text': lambda: render_text_input(label, default_value, key),
        'select': lambda: render_selectbox(label, options, default_value, key),
        'boolean': lambda: render_boolean(label, default_value, key),
        'date': lambda: render_date(label, default_value, key)
    }

    return renderers.get(qtype, lambda: render_text_input(label, default_value, key))()

# OpenAI 4o, 1st Prompt:
# i want to have a funcitonality where i can define all the things that 
# ui need to control like input fields, dropdown boxes, date pickers. 
# can explain the strategy first? 

# OpenAI 4o, last Prompt:
# Cognitive Complexity of functions should not be too high (python:S3776) why am i seeing this for render_question function? 
# why my date picker is until 2015? coz i need dob.