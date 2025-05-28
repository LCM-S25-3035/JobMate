import streamlit as st
from onboarding_ui.onboarding_flow import onboarding_flow
from onboarding_ui.ui_style import load_css

def main():
    load_css("onboarding_ui/styles.css") # Load css

    st.title("JobMate")

    # add side nav bar
    st.sidebar.title("Navigation")

    # region selector
    region_selector = {
        "US": "United States",
        "CA": "Canada"
    }
    region_keys = list(region_selector.keys())
    current_region = st.sidebar.selectbox("Select Region: ", region_keys, format_func=lambda x: region_selector[x])

    # page selector
    page = st.sidebar.radio("Go to", ["Onboarding", "Reports", "Settings"])
    if page == "Onboarding":
        onboarding_flow(region=current_region, user_id="test_user_123") # hard-coded for testing first
    elif page == "Reports":
        st.write("Reports page coming soon!")
    elif page == "Settings":
        st.write("Settings page coming soon!")

if __name__ == "__main__":
    main()

# Reference:
# OpenAI 4o, first prompt: 
# Want to add a nav bar. can show me an example code? 

# OpenAI 4o, last prompt: 
# Wnat to add the region selector drop down. 