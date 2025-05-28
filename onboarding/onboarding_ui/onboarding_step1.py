import streamlit as st
from onboarding_api.services.onboarding_service import get_questions_by_region, load_user_answers
from onboarding_ui.ui_widgets import render_question

def render_step1(region: str, user_id: str) -> bool:
    try:
        questions = get_questions_by_region(region)
    except Exception as e:
        st.error(f"Error loading questions from DB: {e}")
        return False

    step1_questions = [q for q in questions if str(q.get("step", "")) == "1"]

    saved_answers = {}
    try:
        saved_answers = load_user_answers(user_id, region) or {}
    except Exception as e:
        st.warning(f"Could not load saved answers: {e}")

    if "answers" not in st.session_state:
        st.session_state.answers = saved_answers.copy()

    all_required_filled = True

    for q in step1_questions:
        key = q.get("question_id")
        q["question_text"] = q.get("question_text", "").replace("{region_name}", region)
        default_value = st.session_state.answers.get(key, "")
        val = render_question(q, default_value)
        st.session_state.answers[key] = val

        required = q.get("required", False)
        if isinstance(required, str):
            required = required.upper() == "TRUE"

        if required and (val is None or (isinstance(val, str) and val.strip() == "")):
            all_required_filled = False

    if not all_required_filled:
        st.warning("Please fill all required (*) questions before continuing.")

    return all_required_filled

# Reference: 
# OpenAI 4o, First Prompt: 
# Now that i have onboarding_flow where i navigate between steps, 
# how do i display the questions fetched from mongodb and dispaly on ui? 
# Can show an example? 

# OpenAI 4o, Last Prompt: 
# Getting error -> StreamlitDuplicateElementId: There are multiple text_input elements with the same auto-generated ID. When this element is created, it is assigned an internal ID based on the element type and provided parameters. Multiple elements with the same type and parameters will cause this error.
# Getting error -> AttributeError: 'datetime.date' object has no attribute 'strip'
# Getting SonarQube warning -> Two branches in a conditional structure should not have exactly the same implementation (python:S1871)
