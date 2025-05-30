import streamlit as st
from onboarding_api.services.onboarding_service import get_questions_by_region, load_user_answers
from onboarding_ui.ui_widgets import render_question

def render_step2(region: str, user_id: str, validate: bool = False) -> bool:
    try:
        questions = get_questions_by_region(region)
    except Exception as e:
        st.error(f"Error loading questions from DB: {e}")
        return False

    step2_questions = [q for q in questions if str(q.get("step", "")) == "2"]

    saved_answers = {}
    try:
        saved_answers = load_user_answers(user_id, region) or {}
    except Exception as e:
        st.warning(f"Could not load saved answers: {e}")

    if "answers" not in st.session_state:
        st.session_state.answers = saved_answers.copy()

    all_required_filled = True

    for q in step2_questions:
        key = q.get("question_id")
        default_value = st.session_state.answers.get(key, "")
        val = render_question(q, default_value)
        st.session_state.answers[key] = val

        required = q.get("required", False)
        if isinstance(required, str):
            required = required.upper() == "TRUE"

        if required and (val is None or (isinstance(val, str) and val.strip() == "")):
            all_required_filled = False

    st.checkbox(
        label="By providing your contact information and selecting the checkbox, you consent to receive new job alerts and account infmration via email or SMS text messages. You can opt-out at any time by replying 'STOP' to unsubscribe or contacting our customer service. For more information, please visit our Privacy Polilcy and Terms of Service.",
        key="opt-in"
    )
    if validate and not all_required_filled:
        st.warning("Please fill all required (*) questions before continuing.")

    return all_required_filled

# Reference
# OpenAI 4o: Please fill all required (*) fields before continuing. this appeared on step 2 even before i click next button on step 2. explain the error.
# steamlit documentation: "https://docs.streamlit.io/develop/api-reference/widgets/st.checkbox"