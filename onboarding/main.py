import streamlit as st
from onboarding_ui.onboarding_flow import onboarding_flow
from onboarding_ui.ui_helpers import load_css

def main():
    load_css("onboarding_ui/styles.css") # Load css

    st.title("JobMate")

    # add side nav bar
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Onboarding", "Reports", "Settings"])
    if page == "Onboarding":
        onboarding_flow(region="US", user_id="test_user_123") # hard-coded for testing first
    elif page == "Reports":
        st.write("Reports page coming soon!")
    elif page == "Settings":
        st.write("Settings page coming soon!")

if __name__ == "__main__":
    main()

# Reference:
# OpenAI 4o: 
# Want to add a nav bar. can show me an example code? 