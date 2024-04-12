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
from recommendations import create_churn_image
from sklearn.decomposition import PCA
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

#'''Connect to the DB------------------------------------------------------------------------------------------------------------- '''

@st.cache_resource

# def connect_db():
#     password = os.environ.get("MONGODB_PWD") #This is to grab the password from the .env file
#     connection_string = f"mongodb+srv://carlosmebratt:{password}@bdm1003.tnmvwtl.mongodb.net/?retryWrites=true&w=majority"
#     client = MongoClient(connection_string)
#     db=client["bankchurnapp"]    
#     return db

def connect_db():
    # Replace the connection string with the appropriate one for your local MongoDB instance
    connection_string = "mongodb://localhost:27017/"
    client = MongoClient(connection_string)
    db = client["bankchurnapp"]
    return db

#'''Login App Function------------------------------------------------------------------------------------------------------------- '''

def select_signup():
    st.session_state.form = 'signup_form'

def user_update(name, succesful_login):
    st.session_state.username = name
    st.session_state.succesful_login=succesful_login
    
def update_succesful_login(succesful_login):
    st.session_state.succesful_login=succesful_login

def login_app():
    db = connect_db()
    credentials_db=db["credentials"]

    
    # Initialize Session States.
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'form' not in st.session_state:
        st.session_state.form = ''

    if 'succesful_login' not in st.session_state:
        st.session_state.succesful_login = False    
            
    if st.session_state.username != '':
        st.sidebar.markdown(''':blue[You are logged in]''')
        
        logout = st.sidebar.button(label='Log Out')
        if logout:
            # Handle Logout Click
            st.session_state.username = ''  # Set username to empty string
            st.session_state.succesful_login = False  # Set successful_login to False
            st.session_state.form = ''  # Reset form state
            st.sidebar.success("You have successfully logged out!")
            st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar

    

    # Initialize Sing In or Sign Up forms
    if st.session_state.form == 'signup_form' and st.session_state.username == '':

    
        signup_form = st.sidebar.form(key='signup_form', clear_on_submit=True)
        new_username = signup_form.text_input(label='Enter Username*')
        new_user_email = signup_form.text_input(label='Enter Email Address*')
        new_user_pas = signup_form.text_input(label='Enter Password*', type='password')
        user_pas_conf = signup_form.text_input(label='Confirm Password*', type='password')
        note = signup_form.markdown('**required fields*')
        signup = signup_form.form_submit_button(label='Sign Up')
        
        if signup:
            if '' in [new_username, new_user_email, new_user_pas]:
                st.sidebar.error('Some fields are missing')
            else:
                if credentials_db.find_one({'username' : new_username}):
                    st.sidebar.error('This username already exists')
                if credentials_db.find_one({'email' : new_user_email}):
                    st.sidebar.error('This e-mail is already registered')
                else:
                    if new_user_pas != user_pas_conf:
                        st.sidebar.error('Passwords do not match')
                    else:
                        user_update(new_username,True)
                        credentials_db.insert_one({'username' : new_username, 
                                                'email' : new_user_email, 
                                                'password' : new_user_pas,
                                                "creation_time":datetime.now()})
                        

                        # Handle Logout Click
                        st.session_state.username = ''  # Set username to empty string
                        st.session_state.succesful_login = False  # Set successful_login to False
                        st.session_state.form = ''  # Reset form state
                        st.sidebar.success('You have successfully registered!')
                        st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar
                 
    
    
    elif st.session_state.username == '':
        login_form = st.sidebar.form(key='signin_form', clear_on_submit=True)
        username = login_form.text_input(label='Enter Username')
        password = login_form.text_input(label='Enter Password', type='password')        
        

        if credentials_db.find_one({'username' : username, 'password' : password}):
            login = login_form.form_submit_button(label='Sign In', on_click=user_update(username,True))
            if login:
                st.sidebar.success(f"You are logged in as {username.upper()}")  
                st.experimental_rerun() #This is to refresh the page and get rid of the username and password fields from the sidebar
                del password
        else:
            login = login_form.form_submit_button(label='Sign In')
            if login:
                st.sidebar.error("Username or Password is incorrect. Please try again or create an account.")
        

    # 'Create Account' button
    if st.session_state.username == "" and st.session_state.form != 'signup_form':
        signup_request = st.sidebar.button('Create Account', on_click=select_signup)  
    
    return st.session_state.username, st.session_state.succesful_login


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
 
#  def show_recommendations(customer_id):
#     st.session_state['selected_customer'] = customer_id   

# Create a Function to Draw the Donut Chart
def draw_donut_chart(churn_rate):
    fig, ax = plt.subplots()
    size = 0.3
    vals = [churn_rate, 100 - churn_rate]

    ax.pie(vals, radius=1, wedgeprops=dict(width=size, edgecolor='w'))

    ax.set(aspect="equal")
    plt.text(-0.05, 0, f'{churn_rate}%', ha='center', va='center', fontsize=12)
    return fig

# Define a function to handle customer ID click
def handle_customer_click(customer_id):
    st.session_state['selected_customer_id'] = customer_id
    st.session_state['navigation'] = 'customer_detail'

# Main function where the Streamlit app logic is defined
# def main():
#     st.title("Bank Churn Prediction App")

#     # Initialize session state for page navigation and login attempts
#     if 'page' not in st.session_state:
#         st.session_state['page'] = 'login'
#     if 'login_attempt_failed' not in st.session_state:
#         st.session_state['login_attempt_failed'] = False

#     # Login page
#     if st.session_state['page'] == 'login':
#         email = st.text_input("Email address", placeholder="Email")
#         password = st.text_input("Password", type="password")
#         if st.button("Log in"):
#             authenticated, full_name = login(email, password)
#             if authenticated:
#                 st.success(f"Welcome back, {full_name}!")
#             else:
#                 st.error("Email or password is incorrect.")
#                 st.session_state['login_attempt_failed'] = True

#         if st.session_state['login_attempt_failed'] and st.button("Forgot password?"):
#             navigate_to_reset_password()

#         if st.button("Don't have an account? Sign up"):
#             navigate_to_signup()

#     # Signup page
#     elif st.session_state['page'] == 'signup':
#         new_email = st.text_input("Email address", placeholder="Email")
#         new_full_name = st.text_input("Full Name", placeholder="Full Name")
#         new_password = st.text_input("Password", type="password")

#         if st.button("Sign up"):
#             success, message = signup(new_email, new_password, new_full_name)
#             if success:
#                 st.success(message)
#                 navigate_to_login()
#             else:
#                 st.error(message)
#                 if message == "An account with this email already exists.":
#                     # Trigger navigation using session state change instead of button
#                     st.session_state['navigate_to_login'] = True
#                     st.session_state['signup_attempted'] = False  # Reset the signup attempt flag

#         if 'navigate_to_login' in st.session_state and st.session_state['navigate_to_login']:
#             navigate_to_login()

#     # Password reset page
#     elif st.session_state['page'] == 'reset_password':
#         reset_email = st.text_input("Email address", placeholder="Enter your email")
#         new_password = st.text_input("New Password", type="password")

#         if st.button("Reset Password"):
#             success, message = reset_password(reset_email, new_password)
#             if success:
#                 st.success(message + " Please log in with your new password.")
#                 navigate_to_login()
#             else:
#                 st.error(message)
#                 if message == "This email does not exist." and st.button("Create an Account"):
#                     navigate_to_signup()

#     form_content()
        
#'''Funcionality------------------------------------------------------------------------------------------------------------- '''
def form_content(username):
    connect_to_s3 = ConnectToS3()
    
    # st.header('Input data')
     # Select example data
    st.markdown('**Use sample data**')
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
    
    
    st.markdown("**1. Load the clients' data**")
    uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])
    
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, index_col=False)
        input_data = pd.DataFrame(df)
        
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
            st.markdown('**2. Predict churn clients**')
            # Load the saved model
            if st.button('Predict'):
            # Make predictions local this is working on local mode
                model = joblib.load('model.pkl')
                # Load PCA and Clustering models
                pca = joblib.load('pca.pkl')
                clustering_model = joblib.load('clustering_model.pkl')
                recommendations_df = pd.read_csv('recommendations.csv', index_col="Cluster")
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
            
                predicted_data = []
                churned_data = []
                for index, row in input_data.iterrows():
                    id_value = row.iloc[0]  # Use .iloc to get the ID value by position
                    prediction = predictions[index]  # Get the prediction value
                    
                    # Append the data to the list
                    predicted_data.append({
                        'Customer ID': id_value,
                        'Prediction': prediction
                    })
                predicted_df = pd.DataFrame(predicted_data)
                predicted_churn_df=predicted_df
                input_data['Prediction'] = predictions
                
                #''' Start Distribution Pie--------------------------------------------------------------------------------------
                # Count class occurrences (assuming unique class labels)
                # Count the occurrences of each prediction value
                class_counts = predicted_df['Prediction'].value_counts().reset_index()
                class_counts.columns = ['Prediction', 'Count']
                class_counts['Prediction'] = class_counts['Prediction'].replace({1: 'Churned', 0: 'Not Churned'})

                # Create a donut chart using Plotly
                fig = px.pie(class_counts, values='Count', names='Prediction', title='Distribution of Churn Predictions',
                            hole=0.4)  # hole=0.4 makes it a donut chart

                # Display the chart in Streamlit
                st.plotly_chart(fig)
                # '''' End Distribution Pie--------------------------------------------------------------------------------------
                
                #''' Start Donut--------------------------------------------------------------------------------------
                # Main page content based on navigation state
                # if st.session_state['navigation'] == 'home':
                # st.title("Churn Rate Dashboard")
                # churn_rate = 15  # Assumption
                # donut_chart = draw_donut_chart(churn_rate)
                # st.pyplot(donut_chart)

                # st.subheader("Customers Likely to Churn")
                # for index, row in predicted_df.iterrows():
                #     if st.button(f"Customer ID: {row['ID']} - Predicted Churn: {row['Prediction']}"):
                #         handle_customer_click(row['ID'])
                    
                
                # elif st.session_state['navigation'] == 'customer_detail':
                #     st.write(f"Details for customer ID: {st.session_state['selected_customer_id']}")

                # elif st.session_state['navigation'] == 'reports':
                #     st.write("Reports Page Content")

                # elif st.session_state['navigation'] == 'profile':
                #     st.write("Profile Page Content")
                #''' End Donut--------------------------------------------------------------------------------------

                #''' Start Lists All Churned--------------------------------------------------------------------------------------
                # Create tabs for Churned and Not Churned
                # Create DataFrame from your existing predicted data
                # Add the prediction column to input_data for easy filtering (if needed)
                input_data['Prediction'] = predictions

                                # Load PCA and clustering models
                pca = joblib.load('pca.pkl')
                clustering_model = joblib.load('clustering_model.pkl')
                
                # Create tabs for Churned and Not Churned
                tab1, tab2 = st.tabs(["Churned", "Not Churned"])

                # Tab for customers predicted as 'Churned'
                with tab1:
                    churned_df = predicted_df[predicted_df['Prediction'] == 1]
                    if not churned_df.empty:
                        # Ensure Customer ID is correctly formatted as string without commas
                        churned_df['Customer ID'] = churned_df['Customer ID'].astype(str).str.replace(',', '')
                        st.dataframe(churned_df[['Customer ID']])
                    else:
                        st.write("No customers predicted as Churned.")

                with tab2:
                    not_churned_df = predicted_df[predicted_df['Prediction'] == 0]
                    if not not_churned_df.empty:
                        # Similarly, clean the Customer ID for the Not Churned dataframe
                        not_churned_df['Customer ID'] = not_churned_df['Customer ID'].astype(str).str.replace(',', '')
                        st.dataframe(not_churned_df[['Customer ID']])
                    else:
                        st.write("No customers predicted as Not Churned.")
                    
                # try:
                #     # Transform the data using PCA
                #     X_pca = pca.transform(predicted_df.iloc[:, 2:])  # Adjust this to include only the feature columns
                #     predicted_df['Cluster'] = clustering_model.predict(X_pca)
                # except ValueError as e:
                #     st.error(f"Failed to transform data or predict clusters: {e}")
                #     st.stop()
                    
                # Filter to find data where prediction indicates potential churn
                predicted_churn_df = input_data[input_data['Prediction'] == 1]

                # Load PCA model and clustering model
                pca = joblib.load('pca.pkl')
                clustering_model = joblib.load('clustering_model.pkl')

                # Load recommendations data
                recommendations_df = pd.read_csv('recommendations.csv')

                # Filter to identify potential churn
                predicted_churn_df = input_data[input_data['Prediction'] == 1]

                if not predicted_churn_df.empty:
                    print(f'Predicted Churn DataFrame Shape: {predicted_churn_df.shape}')
                    
                    # Transform data using PCA
                    X_pca = pca.transform(predicted_churn_df.iloc[:, 2:])
                    clusters = clustering_model.predict(X_pca)
                    
                    if len(clusters) == len(predicted_churn_df):
                        predicted_churn_df['Cluster'] = clusters
                        # Display results in the app
                        for id_value, cluster in zip(predicted_churn_df['id'], clusters):
                            # Fetch the recommendation safely
                            recommendation_row = recommendations_df[recommendations_df['Cluster'] == cluster]
                            if not recommendation_row.empty:
                                recommendation = recommendation_row['Recommendations'].values[0]
                                st.write(f'Customer Id: {id_value}, Cluster: {cluster}, Recommendation: {recommendation}')
                            else:
                                st.write(f'Customer Id: {id_value}, Cluster: {cluster}, Recommendation: None found for this cluster')
                    else:
                        st.error("Error: Mismatch in the number of predicted clusters and the number of rows in the DataFrame.")
                else:
                    st.write("No churn predictions were made.")


                # tab1, tab2 = st.tabs(["Customers", "Recommendations"])

                # with tab1:
                #     churned_df = predicted_df[predicted_df['Prediction'] == 1]
                #     if not churned_df.empty:
                #         st.dataframe(churned_df[['Customer ID', 'Cluster']])
                #     else:
                #         st.write("No customers predicted as Churned.")

                # with tab2:
                #     if 'selected_customer_id' in st.session_state:
                #         # Assuming recommendations_df is loaded correctly
                #         customer_row = predicted_df[predicted_df['Customer ID'] == st.session_state['selected_customer_id']].iloc[0]
                #         cluster = customer_row['Cluster']
                #         recommendations = recommendations_df.loc[cluster, 'Recommendations']
                #         st.write(f"Recommendations for Customer ID {st.session_state['selected_customer_id']} (Cluster {cluster}):")
                #         st.write(recommendations)
                #     else:
                #         st.write("Select a customer to view recommendations.")


                # Ensure recommendations_df is loaded appropriately
                # recommendations_df = pd.read_csv('path_to_recommendations.csv', index_col="Cluster")

                    
                #''' End Lists All Churned--------------------------------------------------------------------------------------    
    
    
    

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
