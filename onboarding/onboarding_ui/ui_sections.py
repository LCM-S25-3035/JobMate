import streamlit as st
import datetime
import pycountry

MAX_DESC_LENGTH = 3000

def render_experience_fields():
    st.subheader("Work Experience")
    for idx, exp in enumerate(st.session_state.work_experiences):
        st.markdown(f"### Experience {idx + 1}")
        col1, col2 = st.columns(2)
        with col1:
            exp["company"] = st.text_input("Company", value=exp.get("company", ""), key=f"company_{idx}")
            exp["start_date"] = st.date_input(
                "Start Date", value=exp.get("start_date", datetime.date(2020, 1, 1)), key=f"start_{idx}"
            )
        with col2:
            exp["title"] = st.text_input("Title", value=exp.get("title", ""), key=f"title_{idx}")
            exp["end_date"] = st.date_input(
                "End Date", value=exp.get("end_date", datetime.date(2023, 1, 1)), key=f"end_{idx}"
            )
            exp["current"] = st.checkbox("Currently Working Here", value=exp.get("current", False), key=f"current_{idx}")

        countries = sorted([c.name for c in pycountry.countries])
        default_country = exp.get("country", "Canada")
        selected_index = countries.index(default_country) if default_country in countries else 0
        exp["country"] = st.selectbox("Country", countries, index=selected_index, key=f"country_{idx}")

        exp["description"] = st.text_area(
            "Description (max 3000 chars)",
            value=exp.get("description", ""),
            max_chars=MAX_DESC_LENGTH,
            key=f"description_{idx}"
        )

    if st.button("➕ Add Another Experience"):
        st.session_state.work_experiences.append({})

def render_skills_field():
    st.subheader("Skills")
    skills_input = st.text_input(
        "List your skills separated by commas",
        value=st.session_state.answers.get("skills", ""),
        key="skills_input"
    )
    st.session_state.answers["skills"] = skills_input

# Reference: 
# OpenAI 4o: the function is too long, i want to slip into modules. 