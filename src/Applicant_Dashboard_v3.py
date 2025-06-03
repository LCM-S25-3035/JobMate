<<<<<<< Updated upstream
# jobmate_dashboard project - Streamlit + MongoDB + Docker

# File: src/applicant_dashboard_v3.py
import streamlit as st
from streamlit_app.mongo_connection import get_db
from streamlit_app.modules.resume_customization import display_resume_section
from streamlit_app.modules.ai_job_recommender import display_recommendations
from streamlit_app.modules.application_summary import display_application_status
from streamlit_app.modules.reminders import display_reminders
from streamlit_app.modules.history_log import display_application_history
from streamlit_app.modules.performance_metrics import display_metrics
from streamlit_app.modules.personalization_tools import display_tools

st.set_page_config(page_title="JobMate - Applicant Dashboard", layout="wide")

#To link the onboarding and extract data for the applicant profile 
def main():
    st.title("\U0001F4CB JobMate: Applicant Dashboard") 

    menu = [
        "Applicant Profile",
        "Job Recommendations",
        "Application Status",
        "Schedule & Reminders",
        "Application History Log",
        "Personalization Tools",
        "Performance Metrics"
    ]
    choice = st.sidebar.radio("Navigate", menu)

    db = get_db()

    if choice == "Applicant Profile":
        st.subheader("👤 Applicant Profile")
        email = st.text_input("Enter your email:")
        if email:
            user = db["applicants"].find_one({"email": email})
            if user:
                st.write(f"**Name:** {user.get('name')}")
                st.write(f"**Email:** {user.get('email')}")
                st.write(f"**Location:** {user.get('location')}")
                display_resume_section(db, email)
            else:
                st.warning("No profile found.")

    elif choice == "Job Recommendations":
        display_recommendations(db)
        st.markdown("---")
        st.subheader("👻 Ghost Job Detection Prompt")
        st.info("We are actively checking these listings to ensure they're still valid. If you suspect a ghost job (outdated or fake posting), click below.")
        if st.button("Report a Ghost Job"):
            st.success("Thank you for your feedback. Our system will prioritize this listing for validation.")

    elif choice == "Application Status":
        display_application_status(db)

    elif choice == "Schedule & Reminders":
        display_reminders(db)

    elif choice == "Application History Log":
        display_application_history(db)

    elif choice == "Personalization Tools":
        display_tools(db)

    elif choice == "Performance Metrics":
        display_metrics(db)

if __name__ == '__main__':
    main()


# Placeholder files for new modules to be implemented

# File: src/streamlit_app/modules/reminders.py
import streamlit as st

def display_reminders(db):
    st.subheader("🗓️ Schedule & Reminders")
    st.info("This section will show deadlines, interview dates, and follow-up tasks.")


# File: src/streamlit_app/modules/history_log.py
import streamlit as st

def display_application_history(db):
    st.subheader("📜 Application History Log")
    st.info("This section will list all job application actions with timestamps.")


# File: src/streamlit_app/modules/personalization_tools.py
import streamlit as st

def display_tools(db):
    st.subheader("✍️ Personalization Tools")
    st.info("Customize your resume, cover letter, or generate practice questions.")


# File: src/streamlit_app/modules/performance_metrics.py
import streamlit as st

def display_metrics(db):
    st.subheader("📊 Performance Metrics")
    st.info("This section will show stats like total applications, interviews, ATS average.")


# File: requirements.txt
streamlit
pymongo
python-dotenv
pandas


# File: Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "src/applicant_dashboard_v3.py", "--server.port=8501", "--server.address=0.0.0.0"]


# File: .streamlit/secrets.toml
MONGO_URI = "mongodb+srv://<username>:<password>@cluster.mongodb.net/jobmate"


# File: .gitignore
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
=======
# jobmate_dashboard project - Streamlit + MongoDB + Docker

# File: src/applicant_dashboard_v3.py
import streamlit as st
from streamlit_app.mongo_connection import get_db
from streamlit_app.modules.resume_customization import display_resume_section
from streamlit_app.modules.ai_job_recommender import display_recommendations
from streamlit_app.modules.application_summary import display_application_status
from streamlit_app.modules.reminders import display_reminders
from streamlit_app.modules.history_log import display_application_history
from streamlit_app.modules.performance_metrics import display_metrics
from streamlit_app.modules.personalization_tools import display_tools

st.set_page_config(page_title="JobMate - Applicant Dashboard", layout="wide")

#To link the onboarding and extract data for the applicant profile 
def main():
    st.title("\U0001F4CB JobMate: Applicant Dashboard") 

    menu = [
        "Applicant Profile",
        "Job Recommendations",
        "Application Status",
        "Schedule & Reminders",
        "Application History Log",
        "Personalization Tools",
        "Performance Metrics"
    ]
    choice = st.sidebar.radio("Navigate", menu)

    db = get_db()

    if choice == "Applicant Profile":
        st.subheader("👤 Applicant Profile")
        email = st.text_input("Enter your email:")
        if email:
            user = db["applicants"].find_one({"email": email})
            if user:
                st.write(f"**Name:** {user.get('name')}")
                st.write(f"**Email:** {user.get('email')}")
                st.write(f"**Location:** {user.get('location')}")
                display_resume_section(db, email)
            else:
                st.warning("No profile found.")

    elif choice == "Job Recommendations":
        display_recommendations(db)
        st.markdown("---")
        st.subheader("👻 Ghost Job Detection Prompt")
        st.info("We are actively checking these listings to ensure they're still valid. If you suspect a ghost job (outdated or fake posting), click below.")
        if st.button("Report a Ghost Job"):
            st.success("Thank you for your feedback. Our system will prioritize this listing for validation.")

    elif choice == "Application Status":
        display_application_status(db)

    elif choice == "Schedule & Reminders":
        display_reminders(db)

    elif choice == "Application History Log":
        display_application_history(db)

    elif choice == "Personalization Tools":
        display_tools(db)

    elif choice == "Performance Metrics":
        display_metrics(db)

if __name__ == '__main__':
    main()


# Placeholder files for new modules to be implemented

# File: src/streamlit_app/modules/reminders.py
import streamlit as st

def display_reminders(db):
    st.subheader("🗓️ Schedule & Reminders")
    st.info("This section will show deadlines, interview dates, and follow-up tasks.")


# File: src/streamlit_app/modules/history_log.py
import streamlit as st

def display_application_history(db):
    st.subheader("📜 Application History Log")
    st.info("This section will list all job application actions with timestamps.")


# File: src/streamlit_app/modules/personalization_tools.py
import streamlit as st

def display_tools(db):
    st.subheader("✍️ Personalization Tools")
    st.info("Customize your resume, cover letter, or generate practice questions.")


# File: src/streamlit_app/modules/performance_metrics.py
import streamlit as st

def display_metrics(db):
    st.subheader("📊 Performance Metrics")
    st.info("This section will show stats like total applications, interviews, ATS average.")


# File: requirements.txt
streamlit
pymongo
python-dotenv
pandas


# File: Dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "src/applicant_dashboard_v3.py", "--server.port=8501", "--server.address=0.0.0.0"]


# File: .streamlit/secrets.toml
MONGO_URI = "mongodb+srv://<username>:<password>@cluster.mongodb.net/jobmate"


# File: .gitignore
__pycache__/
*.pyc
.env
.streamlit/secrets.toml
>>>>>>> Stashed changes
