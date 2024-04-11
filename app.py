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
            return json.load(f)
    except FileNotFoundError:
        return {}

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

def logout():
    st.session_state['authenticated'] = False
    st.session_state.pop('full_name', None)  # Remove full_name if logged out

def main():
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False

    # Sidebar for login/logout
    with st.sidebar:
        if not st.session_state['authenticated']:
            st.subheader("Login")
            email = st.text_input("Email address", key="login_email")
            password = st.text_input("Password", type="password", key="login_pass")
            if st.button("Log in"):
                authenticated, full_name = login(email, password)
                if authenticated:
                    st.session_state['authenticated'] = True
                    st.session_state['full_name'] = full_name
                else:
                    st.error("Email or password is incorrect.")
            if st.button("Sign up"):
                st.session_state['page'] = 'signup'
        else:
            st.write(f"Welcome, {st.session_state['full_name']}!")
            if st.button("Logout"):
                logout()

    # Main area
    if not st.session_state.get('authenticated', False):
        st.subheader("Please log in to continue.")
    else:
        st.title("Bank Churn Prediction App")
        st.write("You are now logged in and can see this dashboard.")

    # Sign up page handled in main area when not authenticated
    if st.session_state.get('page', '') == 'signup':
        with st.form("signup_form"):
            new_email = st.text_input("Email address", key="signup_email")
            new_full_name = st.text_input("Full Name", key="signup_name")
            new_password = st.text_input("Password", type="password", key="signup_pass")
            signup_button = st.form_submit_button("Sign up")
            if signup_button:
                success, message = signup(new_email, new_password, new_full_name)
                if success:
                    st.success("Signup successful. You can now log in.")
                    st.session_state['page'] = None  # Reset page state after successful signup
                else:
                    st.error(message)

if __name__ == "__main__":
    main()