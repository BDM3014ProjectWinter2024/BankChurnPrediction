import streamlit as st
import json
import hashlib
import churn  

if 'username' not in st.session_state:
    st.session_state.username = ''
if 'useremail' not in st.session_state:
    st.session_state.useremail = ''
if "signedout" not in st.session_state:
    st.session_state["signedout"] = False
if 'signout' not in st.session_state:
    st.session_state['signout'] = False

def app():
    st.title('Welcome to :violet[Bank Churn Prediction]')

    def load_users():
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)


    def load_users():
        try:
            with open('users.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    def save_users(users):
        with open('users.json', 'w') as f:
            json.dump(users, f, indent=4)

    def sign_up_with_email_and_password(email, password, username=None):
        users = load_users()
        if email in users:
            st.warning("Email already exists. Please choose a different one.")
            return

        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        users[email] = {'password': hashed_password, 'username': username}
        save_users(users)
        st.success('Account created successfully!')
        st.markdown('Please Login using your email and password')
        st.balloons()

    def sign_in_with_email_and_password(email=None, password=None):
        users = load_users()
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        if email in users and users[email]['password'] == hashed_password:
            return {'email': email, 'username': users[email]['username']}
        else:
            return None

    def reset_password(email):
        # is not working yet the reset paswword action
        print(f"Reset password requested for email: {email}")

    def f():
        try:
            userinfo = sign_in_with_email_and_password(st.session_state.email_input, st.session_state.password_input)
            if userinfo:
                st.session_state.username = userinfo['username']
                st.session_state.useremail = userinfo['email']
                st.session_state.signedout = True
                st.session_state.signout = True
            else:
                st.warning('Invalid email or password')
        except Exception as e:
            st.warning(f'Login Failed: {e}')

    def t():
        st.session_state.signout = False
        st.session_state.signedout = False
        st.session_state.username = ''

    def forget():
        email = st.text_input('Email')
        if st.button('Send Reset Link'):
            reset_password(email)
            st.success("Password reset email sent successfully.")

    if not st.session_state["signedout"]:
        choice = st.selectbox('Login/Signup', ['Login', 'Sign up'])
        email = st.text_input('Email Address')
        password = st.text_input('Password', type='password')
        st.session_state.email_input = email
        st.session_state.password_input = password

        if choice == 'Sign up':
            username = st.text_input("Enter your unique username")
            if st.button('Create my account'):
                sign_up_with_email_and_password(email=email, password=password, username=username)
        else:
            st.button('Login', on_click=f)
            forget()

    if st.session_state.signout:
        st.text('Name ' + st.session_state.username)
        st.text('Email id: ' + st.session_state.useremail)
        st.button('Sign out', on_click=t)

        churn.run()  

app()


