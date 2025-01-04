import streamlit as st
import pandas as pd
import os
from finance_data import moneymanager

# Initialize session state for login
if 'login_username' not in st.session_state:
    st.session_state.login_username = None
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# CSV file for storing users
CSV_FILE = "users.csv"

# Load users from CSV
def load_users():
    try:
        return pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        st.error("Users file not found!")
        return pd.DataFrame(columns=['username', 'password'])
    except Exception as e:
        st.error(f"Error loading users: {str(e)}")
        return pd.DataFrame(columns=['username', 'password'])

# Check if credentials are valid
def check_credentials(username, password):
    try:
        users_df = load_users()
        return any((users_df['username'] == username) & (users_df['password'] == password))
    except Exception as e:
        st.error(f"Error checking credentials: {str(e)}")
        return False

# Add a new user
def add_user(username, password):
    try:
        users_df = load_users()
        if username in users_df['username'].values:
            return False
        new_user = pd.DataFrame({'username': [username], 'password': [password]})
        users_df = pd.concat([users_df, new_user], ignore_index=True)
        users_df.to_csv(CSV_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error adding user: {str(e)}")
        return False

# Create a user file for storing user transactions
def create_user_file(username):
    user_file = f"{username}_data.csv"
    try:
        if not os.path.exists(user_file):
            df = pd.DataFrame(columns=['date', 'description', 'amount', 'category', 'type', 'payment_method', 'tags'])
            df.to_csv(user_file, index=False)
        return user_file
    except Exception as e:
        st.error(f"Error creating user file: {str(e)}")
        return None

# Set up page configuration
try:
    st.set_page_config(page_title="Finance Insight Hub", layout="wide")
except Exception as e:
    st.error(f"Error setting page config: {str(e)}")

# Display Welcome Message
st.markdown("<h1 style='text-align: center; color: white;'>Welcome to Finance Insight Hub</h1>", unsafe_allow_html=True)

# Handle Login/Signup
if not st.session_state.logged_in:
    try:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.markdown("""
                <style>
                .login-box {
                    background-color: #333333;
                    padding: 30px;
                    border-radius: 10px;
                    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
                    margin: 20px 0;
                }
                </style>
                """, unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["Sign In", "Sign Up"])

            # Sign In
            with tab1:
                username = st.text_input("Username", key="login_username")
                password = st.text_input("Password", type="password", key="login_password")
                if st.button("Login", use_container_width=True):
                    if check_credentials(username, password):
                        st.session_state.logged_in = True
                        st.session_state.login_username = username
                        st.experimental_rerun()
                    else:
                        st.error("Invalid credentials")

            # Sign Up
            with tab2:
                new_username = st.text_input("New Username", key="signup_username")
                new_password = st.text_input("New Password", type="password", key="signup_password")
                confirm_password = st.text_input("Confirm Password", type="password")
                if st.button("Sign Up", use_container_width=True):
                    if new_username and new_password:
                        if new_password != confirm_password:
                            st.error("Passwords don't match!")
                        elif add_user(new_username, new_password):
                            st.success("Account created successfully! Please sign in.")
                        else:
                            st.error("Username already exists!")
                    else:
                        st.error("Please fill all fields")
    except Exception as e:
        st.error(f"Error in login interface: {str(e)}")

else:
    try:
        # On successful login, create or load user file
        if 'user_file' not in st.session_state:
            st.session_state.user_file = create_user_file(st.session_state.login_username)
        user_file = st.session_state.user_file
        st.write(f"User data file: {user_file}")
        # Money Manager Interaction
        moneymanager()
        # Logout functionality
        if st.button("Logout", key="logout"):
            st.session_state.logged_in = False
            st.experimental_rerun()
    except Exception as e:
        st.error(f"Error in logout process: {str(e)}")
