import streamlit as st 
import pandas as pd
import os 
import re 

user_db = "users.csv"

#Load or create user database - code from GPT40

if not os.path.exists(user_db):
    df = pd.DataFrame(columns=["username","password","role"])
    df.to_csv(user_db, index=False)

def load_users():
    return pd.read_csv(user_db)
    df.columns = df.columns.str.strip().str.lower()
    return df

# Save new user - code from GPT40

def save_user(username,password,role):
    df = load_users()
    new_user = pd.DataFrame([[username,password,role]], columns = ["username","password","role"])
    df = pd.concat([df,new_user], ignore_index=True)
    df.to_csv(user_db, index=False)

### Code from : https://medium.com/@wl8380/building-a-secure-and-interactive-user-authentication-system-with-streamlit-adb7a1c89e76

# Password Validation Checking

# Checks the length of the password
# Check if alphanumeric

def password_validity(password):
    if len(password) < 8: 
        return False 
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    return has_letter and has_number

# User and Role Validation Checking

def validate_user(username,password,role):
    if os.path.isfile(user_db):
        data = pd.read_csv(user_db)
        data['username'] = data['username'].astype(str).str.strip()
        data['password'] = data['password'].astype(str).str.strip()
        data['role'] = data['role'].astype(str).str.strip()
        
        username = username.strip().lower()
        password = password.strip()
        role = role.strip() #added myself
        
        user_record = data[(data['username'].str.lower() == username) & (data['password'] == password) & (data['role'] == role)]
        return not user_record.empty
    return False
    

# Streamlit UI # -  code from GPT40

st.title("Welcome to JobMate")

menu = st.sidebar.selectbox("Login or Sign Up", ["Login", "Sign Up"])
role = st.sidebar.selectbox("Are you the..", ["Applicant", "Recruiter"])

st.subheader(f"{menu} as {role.capitalize()}")

username = st.text_input("Username")
password = st.text_input("Password", type="password")

if menu == "Login":
    if st.button("Log In"):
        if validate_user(username, password, role):
            st.success(f"Welcome {username}! You are logged in as a {role}.")
            
            # Route to applicant or recruiter dashboard (insert here )
            
        else:
            st.error("Invalid credentials or role.")
            
elif menu == "Sign Up":
    if st.button("Create Account"):
        if not password_validity(password):
            st.warning("Password must be at least 8 characters and contain both letters and numbers")
        else:
            df = load_users()
            if username.strip().lower() in df['username'].str.lower().values:
                st.warning("Username already exists. Please use a different username")
            else:
                save_user(username,password,role)
                st.success("Account created! You can now log in.")

# http://localhost:8501/