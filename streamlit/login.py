import streamlit as st
import hashlib
import json
import re

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def load_users():
    try:
        with open('users.json', 'r') as f:
            users = json.load(f)
    except FileNotFoundError:
        users = {}
    return users

def signup(email, password, full_name):
    users = load_users()
    if not is_valid_email(email):
        return False, "Please enter a valid email address."
    if email in users:
        return False, "An account with this email already exists."
    users[email] = {'password': hash_password(password), 'full_name': full_name}
    save_users(users)
    return True, "Account created successfully."

def login(email, password):
    users = load_users()
    if email in users and users[email]['password'] == hash_password(password):
        return True, users[email]['full_name']
    return False, ""

def reset_password(email, new_password):
    users = load_users()
    if email in users:
        users[email]['password'] = hash_password(new_password)
        save_users(users)
        return True, "Password reset successful."
    return False, "This email does not exist."

def navigate_to_signup():
    st.session_state['page'] = 'signup'
    st.experimental_rerun()

def navigate_to_reset_password():
    st.session_state['page'] = 'reset_password'
    

def navigate_to_login():
    st.session_state['page'] = 'login'
    st.experimental_rerun()

def main():
    st.sidebar.title("Bank Churn Prediction App")

    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'

    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    if not st.session_state['authenticated']:
        if st.session_state['page'] == 'login':
            email = st.sidebar.text_input("Email address", placeholder="Email")
            password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Log in"):
                authenticated, full_name = login(email, password)
                if authenticated:
                    st.session_state['authenticated'] = True
                    st.session_state['full_name'] = full_name
                else:
                    st.sidebar.error("Email or password is incorrect.")
                    st.sidebar.button("Forgot password?", on_click=navigate_to_reset_password)

            if st.sidebar.button("Don't have an account? Sign up"):
                navigate_to_signup()

        elif st.session_state['page'] == 'signup':
            new_email = st.sidebar.text_input("Email address", placeholder="Email")
            new_full_name = st.sidebar.text_input("Full Name", placeholder="Full Name")
            new_password = st.sidebar.text_input("Password", type="password")
            if st.sidebar.button("Sign up"):
                success, message = signup(new_email, new_password, new_full_name)
                if success:
                    st.sidebar.success(message)
                    navigate_to_login()
                else:
                    st.sidebar.error(message)

        elif st.session_state['page'] == 'reset_password':
            reset_email = st.sidebar.text_input("Email address", placeholder="Enter your email")
            new_password = st.sidebar.text_input("New Password", type="password")
            if st.sidebar.button("Reset Password"):
                success, message = reset_password(reset_email, new_password)
                if success:
                    st.sidebar.success(message + " Please log in with your new password.")
                    navigate_to_login()
                else:
                    st.sidebar.error(message)
                    st.sidebar.button("Create an Account", on_click=navigate_to_signup)
    else:
        st.sidebar.write(f"Hello, {st.session_state['full_name']}!")
        if st.sidebar.button("Logout"):
            st.session_state['authenticated'] = False
            st.session_state.pop('full_name', None)
            navigate_to_login()

    if st.session_state.get('authenticated', False):
        st.image('/workspaces/BankChurnPrediction/group3.png', width=600)
    else:
        st.write("Please log in to see the dashboard.")

if __name__ == "__main__":
    main()
