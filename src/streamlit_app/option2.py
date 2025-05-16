import streamlit as st
import pandas as pd
from pymongo import MongoClient
import json
import os

def run():
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>Resume Database</h1>", unsafe_allow_html=True)
    st.write("Here you can view and manage the resumes in the database.")
    
    try:
        # Get MongoDB connection details from secrets
        MONGO_URI = st.secrets["database"]["MONGODB_URI"]
        MONGO_DB = st.secrets["database"]["MONGODB_DB"]
        MONGO_COLLECTION = st.secrets["database"]["MONGODB_COLLECTION"]
        
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Get all resumes
        resumes = list(collection.find())
        
        if not resumes:
            st.warning("No resumes found in the database.")
            return
            
        # Convert to DataFrame for display
        df = pd.DataFrame(resumes)
        
        # Display the data
        st.dataframe(df)
        
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.error("Please make sure MongoDB is running and the connection details are correct.")
        import traceback
        st.error(f"Traceback: {traceback.format_exc()}")

