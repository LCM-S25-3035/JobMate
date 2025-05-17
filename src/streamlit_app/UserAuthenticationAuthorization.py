import streamlit as st 
import pandas as pd
import os 
import re 

user_db = "users.csv"

# Authored by joyce murillo
#Load or create user database - code from GPT40

if not os.path.exists(user_db):
    df = pd.DataFrame(columns=["username","password","role","email"])
    df.to_csv(user_db, index=False)

# Load users 

def load_users():
    df = pd.read_csv(user_db)
    df.columns = df.columns.str.strip().str.lower()
    return df

# Save new user - code from GPT40

def save_user(username, password, role, email):
    df = load_users()
    new_user = pd.DataFrame([[username,password,role,email]], columns = ["username","password","role","email"])
    df = pd.concat([df,new_user], ignore_index=True)
    df.to_csv(user_db, index=False)

### Code from : https://medium.com/@wl8380/building-a-secure-and-interactive-user-authentication-system-with-streamlit-adb7a1c89e76

# Password Validation Checking

def password_validity(password):
    if len(password) < 8: 
        return False 
    has_letter = any(c.isalpha() for c in password)
    has_number = any(c.isdigit() for c in password)
    return has_letter and has_number

# Email Validation 

def is_valid_email(email):
    regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(regex, email) is not None

# User and Role Validation Checking
# modified code with the help of GPT4.0

def validate_user(username, password, role):
    if os.path.isfile(user_db):
        data = load_users()
        user_record = data[
            (data['username'].str.strip().str.lower() == username.strip().lower()) &
            (data['password'].str.strip() == password.strip()) &
            (data['role'].str.strip().str.lower() == role.strip().lower())]
        return not user_record.empty
    return False
    
# Streamlit UI # -  code from GPT40

st.title("Welcome to JobMate")

menu = st.sidebar.selectbox("Login or Sign Up", ["Login", "Sign Up"])
role = st.sidebar.selectbox("Are you the..", ["Applicant", "Recruiter"])

st.subheader(f"{menu} as {role.capitalize()}")

if menu == "Login":
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Log In"):
        if validate_user(username, password, role):
            st.success(f"🎉 Welcome {username}! You are logged in as a {role}.")
            # TODO: Route to applicant/recruiter dashboard
        else:
            st.error("❌ Invalid credentials or role.")
 
elif menu == "Sign Up":
    with st.form(key='signup_form'):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type='password')
        submit_button = st.form_submit_button(label='Sign Up')

        if submit_button:
            if username and email and password:
                if is_valid_email(email):
                    if password_validity(password):
                        df = load_users()
                        if username.strip().lower() in df['username'].str.lower().values:
                            st.warning("Username already exists. Try logging in.")
                        else:
                            save_user(username, password, role, email)
                            st.success("🎉 Account created! You can now log in.")
                    else:
                        st.error("Password must be at least 8 characters long and contain both letters and numbers.")
                else:
                    st.error("Invalid email address. Please enter a valid email.")
            else:
                st.error("Please fill out all fields.")
 