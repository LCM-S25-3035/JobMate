# File: src/streamlit_app/modules/reminders.py
import streamlit as st

def display_reminders(db):
    st.subheader("🗓️ Schedule & Reminders")
    reminders = db["reminders"].find()
    if reminders:
        for r in reminders:
            st.write(f"📌 **{r.get('title')}** — {r.get('date')}")
    else:
        st.info("No upcoming reminders found.")