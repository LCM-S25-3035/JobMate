import streamlit as st
import pandas as pd
from pymongo import MongoClient
import os

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Select a Job from the Database</h1>", unsafe_allow_html=True)

    # Get MongoDB connection details from secrets
    MONGODB_URI = st.secrets["database"]["MONGODB_URI"]
    MONGO_DB = st.secrets["database"]["MONGODB_DB"]
    MONGO_COLLECTION = st.secrets["database"]["MONGODB_COLLECTION"]
    
    # Connect to MongoDB
    client = MongoClient(MONGODB_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]

    # Ruta al archivo local
    parquet_file = "parquet/jobs_data.parquet"

    # Si existe el archivo .parquet, lo cargamos desde allí
    if os.path.exists(parquet_file):
        df = pd.read_parquet(parquet_file)
    else:
        # Load jobs from MongoDB
        jobs_data = list(collection.find({}))  # Retrieve everything
        df = pd.DataFrame(jobs_data)
        if "_id" in df.columns:
            df["_id"] = df["_id"].astype(str)

    
    # Convert to DataFrame
    # df = df.rename(columns={"_id": "Job ID", "Title": "Job Title", "Provincia": "Province", "Keyword": "Category"})
    # Bug fix
    # Rename columns only if they exist
    rename_map = {}
    if "_id" in df.columns:
        rename_map["_id"] = "Job ID"
    if "Title" in df.columns:
        rename_map["Title"] = "Job Title"
    if "Provincia" in df.columns:
        rename_map["Provincia"] = "Province"
    if "Keyword" in df.columns:
        rename_map["Keyword"] = "Category"
    df = df.rename(columns=rename_map)

    # Bug fix
    # Fill NaN values
    if "Category" in df.columns:
        df["Category"] = df["Category"].fillna("Not Determined")
        df["Category"] = df["Category"].str.title()
    else:
        df["Category"] = "Not Determined"
    if "Province" in df.columns:
        df["Province"] = df["Province"].fillna("Unknown")
        df["Province"] = df["Province"].str.title()
    else:
        df["Province"] = "Unknown"

    # Bug fix
    # Normalize text format
    if "Category" in df.columns:
        df["Category"] = df["Category"].astype(str).str.title()
    else:
        df["Category"] = "Not Determined"

    if "Province" in df.columns:
        df["Province"] = df["Province"].astype(str).str.title()
    else:
        df["Province"] = "Unknown"
    
    # Extract unique categories and cities
    category_options = ["All"] + sorted(df["Category"].unique().tolist()) if "Category" in df.columns else ["All"]
    city_options = ["All"] + sorted(df["Province"].unique().tolist()) if "Province" in df.columns else ["All"]

    # Sidebar Filters
    st.sidebar.header("🔍 Filter Jobs")
        
    selected_city = st.sidebar.selectbox("Select Province", city_options)
    selected_category = st.sidebar.selectbox("Select Category", category_options)

    # Apply Filters
    filtered_df = df.copy()

    if selected_city != "All":
        filtered_df = filtered_df[filtered_df["Province"] == selected_city]

    if selected_category != "All":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]

    # Pagination
    total_rows = len(filtered_df)
    rows_per_page = 20

    if total_rows == 0:
        st.warning("No jobs found matching your filters.")
        return
    elif total_rows <= rows_per_page:
        total_pages = 1
        page_number = 1  # Show all jobs on a single page
    else:
        total_pages = (total_rows // rows_per_page) + (1 if total_rows % rows_per_page > 0 else 0)
        page_number = st.sidebar.slider("Page", 1, total_pages, 1)

    start_idx = (page_number - 1) * rows_per_page
    end_idx = start_idx + rows_per_page

    st.write(f"Showing {start_idx + 1} - {min(end_idx, total_rows)} of {total_rows} jobs")

    # Display paginated DataFrame
    st.dataframe(filtered_df.iloc[start_idx:end_idx].drop(columns=["key_word_app","key_words_app"]))

    # Job Selection
    job_id_input = st.text_input("Enter the Job ID to proceed:", key="job_id_input")

    if job_id_input:
        if job_id_input in filtered_df["Job ID"].astype(str).values:
            st.success(f"✅ Job ID {job_id_input} selected! Proceeding to the next step...")
            st.session_state.selected_job_id = job_id_input
            st.session_state.page = "Option1_4"
            st.rerun()
        else:
            st.error("⚠️ Invalid Job ID. Please enter a valid ID from the table.")

    # Back to Home
    if st.button("⬅️ Back to Home"):
        st.session_state.page = "Home"
        if "app_initialized" in st.session_state:
            del st.session_state.app_initialized
        st.rerun()
