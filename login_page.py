import streamlit as st
import hashlib
import json
import re

# Function definitions

# Validate the email format
def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

# Hash the password for secure storage
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Save the user dictionary to a JSON file
def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

# Load users from the JSON file, returning an empty dict if file doesn't exist
def load_users():
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    return users

# Register a new user, ensuring no duplicate emails
def signup(email, password, full_name):
    users = load_users()
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if email in users:
        return False, "An account with this email already exists."
    users[email] = {'password': hash_password(password), 'full_name': full_name}
    save_users(users)
    return True, "Account created successfully."

# Authenticate a user based on email and password
def login(email, password):
    users = load_users()
    if email in users and users[email]['password'] == hash_password(password):
        return True, users[email]['full_name']
    return False, ""

# Reset the user's password if the email exists
def reset_password(email, new_password):
    users = load_users()
    if email in users:
        users[email]['password'] = hash_password(new_password)
        save_users(users)
        return True, "Password reset successfully."
    return False, "This email does not exist."

# Main function where the Streamlit app logic is defined
def main():
    st.title("Bank Churn Prediction App")

    # Initialize session state for page navigation and login attempts
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'login_attempt_failed' not in st.session_state:
        st.session_state['login_attempt_failed'] = False

    # Functions to handle navigation
    def navigate_to_signup():
        st.session_state['page'] = 'signup'
    
    def navigate_to_reset_password():
        st.session_state['page'] = 'reset_password'

    # Login page
    if st.session_state['page'] == 'login':
        email = st.text_input("Email address", placeholder="Email")
        password = st.text_input("Password", type="password")
        if st.button("Log in"):
            authenticated, full_name = login(email, password)
            if authenticated:
                st.success(f"Welcome back, {full_name}!")
                st.session_state['login_attempt_failed'] = False
            else:
                st.error("Email or password is incorrect.")
                st.session_state['login_attempt_failed'] = True
        
        # Display 'Forgot password?' button after a failed login attempt
        if st.session_state['login_attempt_failed']:
            if st.button("Forgot password?"):
                navigate_to_reset_password()
                
        if st.button("Don't have an account? Sign up"):
            navigate_to_signup()

    # Signup page
    elif st.session_state['page'] == 'signup':
        new_email = st.text_input("Email address", placeholder="Email", key="signup_email")
        new_full_name = st.text_input("Full Name", placeholder="Full Name", key="signup_full_name")
        new_password = st.text_input("Password", type="password", key="signup_password")
        if st.button("Sign up"):
            success, message = signup(new_email, new_password, new_full_name)
            if success:
                st.success(message)
                st.session_state['page'] = 'login'
            else:
                st.error(message)

    # Password reset page
    elif st.session_state['page'] == 'reset_password':
        reset_email = st.text_input("Email address", placeholder="Enter your email", key="reset_email")
        new_password = st.text_input("New Password", type="password", key="new_password")
        if st.button("Reset Password"):
            success, message = reset_password(reset_email, new_password)
            if success:
                st.success(message)
                st.session_state['page'] = 'login'
            else:
                st.error(message)
                if st.button("Create an account"):
                    navigate_to_signup()

# Run the main function when the script is executed
if __name__ == "__main__":
    main()
