import streamlit as st
from onboarding_ui.onboarding_step1 import render_step1
from onboarding_ui.onboarding_step2 import render_step2
from onboarding_ui.onboarding_step3 import render_step3
from onboarding_api.services.onboarding_service import save_user_answers

TOTAL_STEPS = 3 # set total steps

def show_stepper(current_step: int, steps: list):
    step_html = '<ul class="stepper">'
    for i, label in enumerate(steps, 1):
        active = "active" if i == current_step else ""
        step_html += f'<li class="{active}"><span>{label}</span></li>'
    step_html += '</ul>'
    st.markdown(step_html, unsafe_allow_html=True)

def onboarding_flow(region: str, user_id: str):

    if "step" not in st.session_state:
        st.session_state.step = 1

    # Show progress bar and step labels at the top
    steps = ["Key Questions", "Resume", "Review"]
    show_stepper(st.session_state.step, steps)

    can_proceed = False # fix UnboundLocalError

    # Navigating between steps
    if st.session_state.step == 1:
        can_proceed = render_step1(region, user_id)
    elif st.session_state.step == 2:
        can_proceed = render_step2(region, user_id)
    elif st.session_state.step == 3:
        can_proceed = render_step3()


    # Add spacer to push buttons to the bottom
    st.markdown("<div style='height: 5vh;'></div>", unsafe_allow_html=True)

    # Create three columns: left for Back, center empty, right for Next
    col1, _, col3 = st.columns([1, 8, 1])

    with col1:
        if st.session_state.step > 1 and st.button("⬅️ Back"):
            st.session_state.step -= 1
            st.rerun()

    with col3:
        if st.button("Next ➡️"):
            if can_proceed:
                save_user_answers(user_id, region, st.session_state.answers)
                if st.session_state.step < TOTAL_STEPS:
                    st.session_state.step += 1
                    st.rerun()
            else:
                st.toast("Please answer all required questions before continuing.")

# Reference:
# OpenAI, 4o first prompt:
# what should be the strategy on splitting the parts so that the functions can be reusable. I need to separate python files, one for the onboarding questions, and another for streamlit ui flow which will show all the onboarding steps (Step 1, Step 2, Step 3), and another .py for showing question on step 1 on streamlit ui.

# OpenAI, 4o last prompt: 
# getting error -> UnboundLocalError: cannot access local variable 'can_proceed' where it is not associated with a value  
# st.warning("Please answer all required questions before continuing.")instead of this, can we do a pop up? 