import time
import streamlit as st
from datetime import datetime
import pandas as pd
import numpy as np
import pickle
import plotly.express as px
from io import StringIO
import os
import joblib
import boto3
import botocore
from s3conn import S3Utils, ConnectToS3
import hashlib
import json
import re



# MongoDB libraries
from dotenv import load_dotenv, find_dotenv #Used for import the function to load .env file
import os
from pymongo import MongoClient #Used to create the connection
load_dotenv(find_dotenv()) #Shorcut to load the enviroment file



#'''Streamlit settings------------------------------------------------------------------------------------------------------------- '''

# Page title
st.set_page_config(page_title='Bank Churn App', 
                   page_icon='🤖', layout="wide", 
                   initial_sidebar_state="expanded")

#'''Login Page------------------------------------------------------------------------------------------------------------- '''

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

# Load users from the JSON file, returning an empty dict if the file doesn't exist
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
        return True, "Password reset successful."
    return False, "This email does not exist."

# Functions to handle navigation
def navigate_to_signup():
    st.session_state['page'] = 'signup'
    st.rerun()

def navigate_to_reset_password():
    st.session_state['page'] = 'reset_password'
    st.rerun()

def navigate_to_login():
    st.session_state['page'] = 'login'
    st.rerun()

# Main function where the Streamlit app logic is defined
def main():
    st.title("Bank Churn Prediction App")

    # Initialize session state for page navigation and login attempts
    if 'page' not in st.session_state:
        st.session_state['page'] = 'login'
    if 'login_attempt_failed' not in st.session_state:
        st.session_state['login_attempt_failed'] = False

    # Login page
    if st.session_state['page'] == 'login':
        email = st.text_input("Email address", placeholder="Email")
        password = st.text_input("Password", type="password")
        if st.button("Log in"):
            authenticated, full_name = login(email, password)
            if authenticated:
                st.success(f"Welcome back, {full_name}!")
            else:
                st.error("Email or password is incorrect.")
                st.session_state['login_attempt_failed'] = True

        if st.session_state['login_attempt_failed'] and st.button("Forgot password?"):
            navigate_to_reset_password()

        if st.button("Don't have an account? Sign up"):
            navigate_to_signup()

    # Signup page
    elif st.session_state['page'] == 'signup':
        new_email = st.text_input("Email address", placeholder="Email")
        new_full_name = st.text_input("Full Name", placeholder="Full Name")
        new_password = st.text_input("Password", type="password")

        if st.button("Sign up"):
            success, message = signup(new_email, new_password, new_full_name)
            if success:
                st.success(message)
                navigate_to_login()
            else:
                st.error(message)
                if message == "An account with this email already exists.":
                    # Trigger navigation using session state change instead of button
                    st.session_state['navigate_to_login'] = True
                    st.session_state['signup_attempted'] = False  # Reset the signup attempt flag

        if 'navigate_to_login' in st.session_state and st.session_state['navigate_to_login']:
            navigate_to_login()

    # Password reset page
    elif st.session_state['page'] == 'reset_password':
        reset_email = st.text_input("Email address", placeholder="Enter your email")
        new_password = st.text_input("New Password", type="password")

        if st.button("Reset Password"):
            success, message = reset_password(reset_email, new_password)
            if success:
                st.success(message + " Please log in with your new password.")
                navigate_to_login()
            else:
                st.error(message)
                if message == "This email does not exist." and st.button("Create an Account"):
                    navigate_to_signup()


#'''Funcionality------------------------------------------------------------------------------------------------------------- '''
def form_content(username):
    connect_to_s3 = ConnectToS3()
    
    st.header('Input data')
    st.markdown("**1. Load the clients' data**")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=False)
        input_data = pd.DataFrame(df)
    
    # Select example data
    st.markdown('**2. Use example data**')
    # # Download example data
    @st.cache_data
    def convert_df(input_df):
        return input_df.to_csv(index=False).encode('utf-8')
    
    # Get the csv/dataset from S3
    if connect_to_s3.s3_utils.check_file_exists(connect_to_s3.output_file_key_data_feature_engineering):
        example_csv = connect_to_s3.s3_utils.read_csv_from_s3(connect_to_s3.output_file_key_data_feature_engineering)
        csv = convert_df(example_csv)

    st.download_button(
        label="Download example CSV",
        data=csv, 
        file_name='bank_churn_dataset.csv',
        mime='text/csv',
    )
    
    # Initiate the model building process
    if uploaded_file:  
        st.subheader('Processing the data')
        st.write('Processing in progress...')

        # Placeholder for model building process
        with st.spinner('Wait for it...'):
            time.sleep(2)

        #st.write('Customer predictions are now complete!')
        st.markdown(''':blue[Customer data has been loaded!]''')

        # st.dataframe(data=df, use_container_width=True)


    #'''--------------------------------------------------------------------------------------
    
    # st.markdown('**2. Load the saved model**')
    # # Load the saved model
    # uploaded_pkl = st.file_uploader("Upload .pkl file", type=["pkl"])

    # # Check if a file is uploaded
    # if uploaded_pkl is not None:
    #     st.write("File uploaded successfully!")

    #     try:
    #         # Load the model from the file
    #         loaded_model = pd.read_pickle(uploaded_pkl)
    #         st.success("Model loaded successfully!")

            
    #     except Exception as e:
    #         st.error(f"Error loading .pkl file: {e}")

    # else:
    #     st.info("Please upload a .pkl file.")

    

    #'''--------------------------------------------------------------------------------------
    st.markdown('**3. Predict churn clients**')
    # Load the saved model
    if st.button('Predict'):
        # # Convert input data to numpy array
        #input_data_np = np.array(df)  # Adjust input data format as needed

       # Make predictions local this is working on local mode
        model = joblib.load('model.pkl')
        #Predict the data
        predictions = model.predict(input_data)
        
        # Make predictions s3
        # if connect_to_s3.s3_utils.check_file_exists(connect_to_s3.output_file_key_data_random_forest_pkl):
        # # Load the model directly from S3
        #     model = connect_to_s3.load_model_from_s3(connect_to_s3.output_file_key_data_random_forest_pkl)

        #     predictions = model.predict(input_data)
        #     st.write("Model file not found in S3.")
        #     for index, row in input_data.iterrows():
        #         first_feature_name = row.index[0]  # Get the name of the first feature
        #         first_feature_value = row[0]  # Get the value of the first feature
        #         st.write(f'First Feature: {first_feature_name}: {first_feature_value} -> Prediction: {predictions[index]}')
        # else:
        #     st.write("Model file not found in S3.")

        
       
        data = []
        for index, row in input_data.iterrows():
            id_value = row.iloc[0]  # Use .iloc to get the ID value by position
            prediction = predictions[index]  # Get the prediction value

            # Append the data to the list
            data.append({
                'ID': id_value,
                'Prediction': prediction
            })
        predicted_df = pd.DataFrame(data)
        
         #'''--------------------------------------------------------------------------------------

        st.title("Class Distribution Pie Chart")

        # Count class occurrences (assuming the column with class labels is named 'Prediction')
        class_counts = predicted_df['Prediction'].value_counts().reset_index()
        class_counts.columns = ['Clients', 'Count']

        # Customize class labels
        class_counts['Class'] = class_counts['Class'].map({1: 'Churned', 0: 'Not Churned'})

        # Display data (optional)
        st.write(class_counts)  # Use st.write to display the DataFrame

        # Create the pie chart
        fig = px.pie(class_counts, values='Count', names='Class', title='Distribution of Classes')

        # Display the chart
        st.plotly_chart(fig)
        

   


#'''Main Function------------------------------------------------------------------------------------------------------------- '''
    

def main():
    # Initialize Session States.
    succesful_login=False
    username, succesful_login=login_app()

    st.title('Machine Learning App for Bank Churn Prediction')
    

    if succesful_login == False:        
        st.subheader("Please use the sidebar on the left to log in or create an account.")
        st.image('image1.png')

    else:
        with st.sidebar:             
            st.header(f"Welcome {username} !")
        
        form_content(username)


#'''Sidebar------------------------------------------------------------------------------------------------------------- '''

    
    with st.sidebar:

        with st.expander('About this app / Instructions'):
                    st.markdown('**What can this app do?**')
                    st.info('This app allow users to load a bank .csv file and use it to build a machine learning model to predict churn. The app also recomends actions to reduce churn.')

                    st.markdown('**How to use the app?**')
                    st.warning('To engage with the app, please login or create an account and then 1. Select a data set and 2. Click on "Run the model". As a result, this would initiate the ML model and data processing.')

                    st.markdown('**Under the hood**')
                    st.markdown('Data sets:')
                    st.code('''- You can upload your own data set or use the example data set provided in the app.
                    ''', language='markdown')
                    
                    st.markdown('Libraries used:')
                    st.code('''
                            * Pandas for data wrangling  
                            * Scikit-learn
                            * XGBoost for machine learning
                            * Streamlit for user interface
                    ''', language='markdown')

# Call the main function
if __name__ == '__main__':
    main()
